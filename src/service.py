"""
OpenFGA Service - Handles all interactions with OpenFGA (using direct HTTP calls)
"""
import asyncio
import aiohttp
import json
from typing import List, Optional, Dict, Any
from config import OPENFGA_API_URL, OPENFGA_STORE_ID, OPENFGA_MODEL_ID


class OpenFGAService:
    """Service for interacting with OpenFGA"""
    
    def __init__(self):
        self.session = None
        self.store_id = OPENFGA_STORE_ID
        self.model_id = OPENFGA_MODEL_ID
        
    async def initialize(self):
        """Initialize the OpenFGA service"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Check if configured store exists, if not create new one
            await self._ensure_store()
            
            # Check if configured model exists, if not create new one  
            await self._ensure_model()
            
            print(f"Using OpenFGA store: {self.store_id}")
            print(f"Using authorization model: {self.model_id}")
                
        except Exception as e:
            print(f"Failed to initialize OpenFGA service: {e}")
            raise
    
    async def _ensure_store(self):
        """Ensure we have a valid store"""
        # First try to use configured store
        if self.store_id and self.store_id != "01JYYK7BG878R7NVQRECYFT5C4":  # Skip default placeholder
            try:
                async with self.session.get(f"{OPENFGA_API_URL}/stores/{self.store_id}") as response:
                    if response.status == 200:
                        print(f"Using existing store: {self.store_id}")
                        return
            except:
                pass
        
        # Look for existing rebecca-store by name
        try:
            async with self.session.get(f"{OPENFGA_API_URL}/stores") as response:
                if response.status == 200:
                    data = await response.json()
                    for store in data.get("stores", []):
                        if store.get("name") == "rebecca-store":
                            self.store_id = store["id"]
                            print(f"Found existing rebecca-store: {self.store_id}")
                            return
        except:
            pass
        
        # Store doesn't exist, create a new one
        try:
            payload = {"name": "rebecca-store"}
            async with self.session.post(f"{OPENFGA_API_URL}/stores", json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    self.store_id = data["id"]
                    print(f"Created new store: {self.store_id}")
                else:
                    raise Exception(f"Failed to create store: {response.status}")
        except Exception as e:
            print(f"Failed to create store: {e}")
            raise
    
    async def _ensure_model(self):
        """Ensure we have a valid authorization model"""
        # Check if configured model exists (skip placeholder)
        if self.model_id and self.model_id != "01JYYK7D1CY0KMVPJV6HVYZMEH" and self.store_id:
            try:
                url = f"{OPENFGA_API_URL}/stores/{self.store_id}/authorization-models/{self.model_id}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        print(f"Using existing model: {self.model_id}")
                        return
            except:
                pass
        
        # Look for existing model in this store
        if self.store_id:
            try:
                url = f"{OPENFGA_API_URL}/stores/{self.store_id}/authorization-models"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("authorization_models", [])
                        if models:
                            # Use the latest model
                            self.model_id = models[0]["id"]
                            print(f"Using existing model from store: {self.model_id}")
                            return
            except:
                pass
        
        # Model doesn't exist, create a new one
        model_json = {
            "schema_version": "1.1",
            "type_definitions": [
                {
                    "type": "user"
                },
                {
                    "type": "group",
                    "relations": {
                        "member": {"this": {}}
                    },
                    "metadata": {
                        "relations": {
                            "member": {
                                "directly_related_user_types": [{"type": "user"}]
                            }
                        }
                    }
                },
                {
                    "type": "folder",
                    "relations": {
                        "owner": {"this": {}},
                        "viewer": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [{"type": "user"}]
                            },
                            "viewer": {
                                "directly_related_user_types": [{"type": "user"}]
                            }
                        }
                    }
                },
                {
                    "type": "doc",
                    "relations": {
                        "owner": {"this": {}},
                        "viewer": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [{"type": "user"}]
                            },
                            "viewer": {
                                "directly_related_user_types": [{"type": "user"}]
                            }
                        }
                    }
                }
            ]
        }
        
        try:
            url = f"{OPENFGA_API_URL}/stores/{self.store_id}/authorization-models"
            async with self.session.post(url, json=model_json) as response:
                if response.status == 201:
                    data = await response.json()
                    self.model_id = data["authorization_model_id"]
                    print(f"Created new model: {self.model_id}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create model: {response.status} - {error_text}")
        except Exception as e:
            print(f"Failed to create authorization model: {e}")
            raise
    
    async def write_tuple(self, user: str, relation: str, object_ref: str) -> bool:
        """Write a relationship tuple to OpenFGA"""
        try:
            url = f"{OPENFGA_API_URL}/stores/{self.store_id}/write"
            payload = {
                "writes": {
                    "tuple_keys": [
                        {
                            "user": user,
                            "relation": relation,
                            "object": object_ref
                        }
                    ]
                }
            }
            
            async with self.session.post(url, json=payload) as response:
                return response.status == 200
            
        except Exception as e:
            print(f"Failed to write tuple: {e}")
            return False
    
    async def delete_tuple(self, user: str, relation: str, object_ref: str) -> bool:
        """Delete a relationship tuple from OpenFGA"""
        try:
            url = f"{OPENFGA_API_URL}/stores/{self.store_id}/write"
            payload = {
                "deletes": {
                    "tuple_keys": [
                        {
                            "user": user,
                            "relation": relation,
                            "object": object_ref
                        }
                    ]
                }
            }
            
            async with self.session.post(url, json=payload) as response:
                return response.status == 200
            
        except Exception as e:
            print(f"Failed to delete tuple: {e}")
            return False
    
    async def check_permission(self, user: str, relation: str, object_ref: str) -> bool:
        """Check if a user has a specific relation to an object"""
        try:
            url = f"{OPENFGA_API_URL}/stores/{self.store_id}/check"
            payload = {
                "tuple_key": {
                    "user": user,
                    "relation": relation,
                    "object": object_ref
                }
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("allowed", False)
                return False
            
        except Exception as e:
            print(f"Failed to check permission: {e}")
            return False
    
    async def read_tuples(self, user: Optional[str] = None, relation: Optional[str] = None, 
                         object_ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read tuples from OpenFGA with optional filtering"""
        try:
            url = f"{OPENFGA_API_URL}/stores/{self.store_id}/read"
            payload = {"tuple_key": {}}
            
            if user:
                payload["tuple_key"]["user"] = user
            if relation:
                payload["tuple_key"]["relation"] = relation
            if object_ref:
                payload["tuple_key"]["object"] = object_ref
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert tuples to dict format matching current API
                    tuples = []
                    for tuple_data in data.get("tuples", []):
                        tuples.append({
                            'user': tuple_data["key"]["user"],
                            'relation': tuple_data["key"]["relation"],
                            'object': tuple_data["key"]["object"]
                        })
                    
                    return tuples
                return []
            
        except Exception as e:
            print(f"Failed to read tuples: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if OpenFGA is healthy and accessible"""
        try:
            async with self.session.get(f"{OPENFGA_API_URL}/stores") as response:
                return response.status == 200
        except Exception:
            return False
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()


# Global instance
openfga_service = OpenFGAService()


async def get_openfga_service() -> OpenFGAService:
    """Get the initialized OpenFGA service"""
    if openfga_service.session is None:
        await openfga_service.initialize()
    return openfga_service
