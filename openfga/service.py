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
            print(f"Using existing OpenFGA store: {self.store_id}")
            print(f"Using existing authorization model: {self.model_id}")
                
        except Exception as e:
            print(f"Failed to initialize OpenFGA service: {e}")
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
