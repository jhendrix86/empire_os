FROM python:3.11-slim

# Preserve "empire_os" as a real package directory under /app so both
# "from empire_os.engines import ..." and bare "orchestrator.*"/"operators.*"
# imports resolve, matching the dual sys.path pattern used on the host
# (see tests/test_integration.py and api.py's own sys.path setup).
WORKDIR /app

COPY requirements.txt empire_os/requirements.txt
RUN pip install --no-cache-dir -r empire_os/requirements.txt

COPY . empire_os/

EXPOSE 8100
CMD ["uvicorn", "empire_os.api:app", "--host", "0.0.0.0", "--port", "8100"]
