#!/bin/bash
cd /home/site/wwwroot
source antenv/bin/activate
cd src
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true
