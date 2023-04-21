from fastapi import APIRouter

from yao.function.company.main import router as company
from yao.function.user.main import router as user
from yao.function.permission.main import router as permission
from yao.function.appointment.main import router as appointment
from yao.function.department.main import router as department
from yao.function.annex.main import router as annex
from yao.function.log.main import router as log

router = APIRouter()
router.include_router(company)
router.include_router(user)
router.include_router(permission)
router.include_router(appointment)
router.include_router(department)
router.include_router(annex)
router.include_router(log)
