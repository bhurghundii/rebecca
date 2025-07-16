User Managers are tools that handle permissions for users and groups — in other words, they help manage authorisation.

Authorisation determines whether someone is allowed to perform a certain action. A simple example is allowing an admin user to access an admin dashboard.

However, authorisation is a complex problem because of its granularity. It ranges from broad questions like “which user roles can access which parts of the app?” to extremely specific ones like “can this user access this particular document?”

Because of this complexity, User Managers are common in public, consumer-facing software, but they’re rarely built for internal enterprise applications, where access needs can be just as nuanced — if not more so.

# Why is this a problem?
It’s hard to justify taking time away from the product roadmap to build a dedicated user manager — especially for internal apps that will only have a few hundred users.

In a conversation with a Product Owner at a well-known Fortune 500 payment solutions company, they shared that these kinds of authorisation problems “aren’t even worked on.” The reason? Implementing robust access control systems takes significant time, and the manual effort involved is often seen as a distraction from more immediate deliverables.

# FGA - The “Almost There” Tool
There’s been impressive progress in the world of authorisation modelling, especially with policy languages like OpenFGA and Amazon Cedar.

But in practice — and confirmed by conversations with developers working on auth systems — these tools still leave a significant gap. While they handle the policy engine side well, the burden of integration and orchestration falls entirely on the developer. You're left stitching things together, building management interfaces, and tailoring the system to fit the specifics of your app — which can be complex and time-consuming.

<img width="1422" height="560" alt="image" src="https://github.com/user-attachments/assets/e2083f49-e279-4f57-bfd9-731dc818ae78" />

# Why Is This Not Being Worked On?
If I had to speculate, it’s because it’s incredibly boring. Compliance is boring.

The result? Most teams either hack something together with hardcoded roles… or avoid tackling the problem altogether.

# Filling the Gap
Platforms like Oso have acknowledged an important reality: there’s still a lot of heavy lifting between having a policy engine and actually integrating it into your application in a usable, maintainable way. They focus on simplifying authorisation logic, but even then, developers are left bridging the gap between a powerful engine and the specifics of their product.

Another example is Unleash, an open-source feature flag platform. While it's not directly tied to authorisation, it shares a similar goal: dynamic control over application behaviour at runtime. I like Unleash because it’s open source and you can host it in your internal network very easily.

What these tools have in common is that we’re starting to see plug-and-play solutions emerge for common but previously complex infrastructure problems — whether it’s feature gating or policy enforcement.

In my experience, this gap becomes especially painful in environments where compliance, auditability, and data access control really matter — often the case in enterprise software. Teams in these settings need robust fine-grained access control, but they also need to justify implementing solutions that aren’t traditionally associated with enterprise software. Tools that can solve these problems often come with overhead, and for many teams, it's difficult to make a case for their inclusion when other priorities take precedence.

The Bet: 90% of Use Cases Are About Letting Users Access an Admin Page
For most organisations using FGA in enterprise settings, the primary concern isn't scaling permissions for billions of users. Rather, product owners and tech leads are more focused on compliance and managing permissions at a more granular level. In these environments, the real challenge is ensuring that the right people have the right level of access — often just to an admin page or specific internal resource — and making sure those permissions are auditable and compliant with regulations.

<img width="584" height="222" alt="image" src="https://github.com/user-attachments/assets/f0fc6cd1-923e-42d7-9326-08176b682d24" />

# Introducing Rebecca: The Missing User Manager
For teams building systems with a smaller set of users, such as internal enterprise applications, and who need to care about data control, the need for a simple yet powerful admin panel becomes clear.

Teams need a way to control what users can do, what features they can access, and what documents they can view — all while ensuring compliance and ease of management. Standard stuff.

Rebecca is an open-source solution designed to fill that gap. It’s based on OpenFGA and comes with a pre-built Admin Panel UI, so developers don’t waste time creating tools from scratch.

Rebecca is a side car that sits alongside your apps in your network and developers use the API to do all sorts of checks.

You can easily self-host it via Docker, making it flexible and easy to deploy in your own environment. With Rebecca, teams can focus on building their core product instead of spending valuable time on authorisation and user management tooling.
