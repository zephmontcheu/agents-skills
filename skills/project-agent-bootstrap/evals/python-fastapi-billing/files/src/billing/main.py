from fastapi import FastAPI

from billing.invoices import router

app = FastAPI(title="billing-api")
app.include_router(router)
