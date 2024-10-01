# FASTAPI-MODULARIZED

run fastapi without logs
uvicorn aws_image_manager.main:app --reload

## run fastapi with logs
uvicorn aws_image_manager.main:app --reload --log-config log.ini
