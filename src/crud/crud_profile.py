from src.crud.base import CRUDBase
from src.models.profile import SocialProfile
from src.schemas.profile import SocialProfileCreate

class CRUDProfile(CRUDBase[SocialProfile, SocialProfileCreate, SocialProfileCreate]):
    # For now, the base methods are sufficient.
    # We might add methods here later like `get_by_platform_user_id`.
    pass

profile = CRUDProfile(SocialProfile)
