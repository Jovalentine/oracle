FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY --chown=user . $HOME/app

# Create necessary folders with write permissions
RUN mkdir -p data/uploads data/outputs data/reports data/videos

# Expose port 7860 (Hugging Face Default)
ENV PORT=7860
EXPOSE 7860

# Command to start the app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app