from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, categories, chatbot, health, interactions, listings, recommendations, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Management"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(listings.router, prefix="/listings", tags=["Listings"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Moderation"])
api_router.include_router(interactions.router, tags=["Interactions & Inquiries"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["AI Chatbot"])
