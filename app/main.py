from fastapi import FastAPI

from app.api.admin_routes import router as admin_router
from app.api.routes import API_V1_PREFIX, NAME, VERSION, router

app = FastAPI(title=NAME, version=VERSION)

# The same handlers are served twice: under /api/v1 as the documented API, and
# on the original paths so clients written before versioning keep working. The
# legacy mount stays out of the schema to keep the documentation unambiguous.
app.include_router(router, prefix=API_V1_PREFIX, tags=["v1"])
app.include_router(router, include_in_schema=False)

# Administration lives under the versioned prefix only: it is a new surface,
# so there is no older path to keep working.
app.include_router(admin_router, prefix=API_V1_PREFIX)
