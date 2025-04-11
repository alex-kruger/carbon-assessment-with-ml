FROM continuumio/miniconda3:23.10.0-1

WORKDIR /app

COPY requirements.txt .

# Create environment and install dependencies
RUN conda create -n parakeetenv python=3.11.7
RUN conda run -n parakeetenv pip install -r requirements.txt

COPY . .

EXPOSE 5000

# Run inside the created environment
CMD ["conda", "run", "--no-capture-output", "-n", "parakeetenv", "python", "app.py"]
