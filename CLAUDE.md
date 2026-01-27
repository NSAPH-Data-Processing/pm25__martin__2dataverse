# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Data staging pipeline that downloads Washington University PM2.5 satellite data from Box and uploads to Harvard Dataverse. This repo is the "upstream" data source for the aggregation pipeline (pm25_washu_raster2polygon).

## Commands

### Environment Setup
```bash
conda env create -f environment.yaml
conda activate pm25_2dataverse
```

### Download from Box
```bash
python src/download_from_box.py                              # Default: V5GL04 yearly
python src/download_from_box.py dataset=V6GL02               # V6 dataset
python src/download_from_box.py temporal_freq=monthly        # Monthly data
```

### Upload to Dataverse
```bash
python src/upload_to_dataverse.py                            # Upload downloaded files
python src/upload_to_dataverse.py dataset=V6GL02 temporal_freq=monthly
```

## Architecture

### Data Flow
```
Box (ACAG) → download_from_box.py → data/{dataset}/{freq}/*.nc → upload_to_dataverse.py → Dataverse
```

### Scripts
- `download_from_box.py` - Selenium-based Box download, extracts zip, flattens directory
- `upload_to_dataverse.py` - Dataverse API upload with incremental support (skips existing)

### Configuration (Hydra)
- `conf/config.yaml` - Main config with defaults
- `conf/datasets/` - Per-dataset configs with Box URLs and Dataverse credentials

### Key Parameters
- `dataset`: V5GL04, V5GL0502, V6GL02
- `temporal_freq`: yearly, monthly

## Dataverse API

Upload endpoint: `POST /api/datasets/:persistentId/add?persistentId={doi}`
- Header: `X-Dataverse-key: {api_token}`
- Body: multipart form with file

List files: `GET /api/datasets/:persistentId/?persistentId={doi}`
