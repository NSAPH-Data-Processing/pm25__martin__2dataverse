"""
Upload PM2.5 NetCDF files to Harvard Dataverse.

This script uploads files downloaded from Box to a Dataverse dataset.
Run download_from_box.py first to obtain the files.
"""

import os
import glob
import hydra
import logging
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def upload_file(filepath: str, doi: str, server_url: str, api_token: str, directory_label: str = None) -> dict:
    """
    Upload a single file to a Dataverse dataset.

    Args:
        filepath: Path to the file to upload
        doi: Dataset DOI (e.g., "doi:10.7910/DVN/XXXXXX")
        server_url: Dataverse server URL (e.g., "https://dataverse.harvard.edu")
        api_token: Dataverse API token
        directory_label: Optional folder path (e.g., "V5GL04/yearly")

    Returns:
        Response JSON from Dataverse API
    """
    import json

    url = f"{server_url}/api/datasets/:persistentId/add?persistentId={doi}"
    headers = {"X-Dataverse-key": api_token}

    filename = os.path.basename(filepath)
    logger.info(f"Uploading {filename} to {directory_label or 'root'}...")

    with open(filepath, "rb") as f:
        files = {"file": (filename, f)}

        # Add directory label via JSON metadata if specified
        data = {}
        if directory_label:
            data["jsonData"] = json.dumps({"directoryLabel": directory_label})

        response = requests.post(url, headers=headers, files=files, data=data)

    response.raise_for_status()
    return response.json()


def check_existing_files(doi: str, server_url: str, api_token: str) -> set:
    """
    Get list of files already in the Dataverse dataset.

    Returns:
        Set of (directory_label, filename) tuples already uploaded
    """
    url = f"{server_url}/api/datasets/:persistentId/?persistentId={doi}"
    headers = {"X-Dataverse-key": api_token}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    if data.get("status") != "OK":
        raise ValueError(f"Dataverse API error: {data}")

    files = data["data"]["latestVersion"]["files"]
    # Return set of (directory, filename) tuples to handle same filename in different folders
    return {
        (f.get("directoryLabel", ""), f["dataFile"]["filename"])
        for f in files
    }


@hydra.main(config_path="../conf", config_name="config", version_base=None)
def main(cfg):
    """
    Upload downloaded PM2.5 files to Dataverse.
    """

    # Auto-detect dataset name from loaded config (first key in datasets)
    dataset_name = list(cfg.datasets.keys())[0]
    dataset_cfg = cfg.datasets[dataset_name]
    freq_cfg = dataset_cfg[cfg.temporal_freq]
    dataverse_cfg = freq_cfg.dataverse

    # Validate configuration                                                                                                               
    server_url = dataverse_cfg.server_url                                                                                                  
    doi = dataverse_cfg.doi                                                                                                                
    # Check environment variable first, then fall back to config                                                                           
    api_token = os.environ.get("DATAVERSE_API_TOKEN") or dataverse_cfg.api_token

    if not api_token:
        raise ValueError(
            "Dataverse API token is required for uploads. "
            "Set it in conf/datasets/*.yaml or via environment variable."
        )

    if "XXXXXXX" in doi:
        raise ValueError(
            f"Dataverse DOI is a placeholder: {doi}\n"
            "Create a dataset on Dataverse first and update the config with the real DOI."
        )

    # Find files to upload
    source_dir = f"{cfg.download_dir}/{dataset_name}/{cfg.temporal_freq}"
    file_pattern = f"{source_dir}/*.nc"
    files_to_upload = sorted(glob.glob(file_pattern))

    if not files_to_upload:
        logger.error(f"No NetCDF files found in {source_dir}")
        logger.error("Run download_from_box.py first to download the data.")
        return

    # Folder structure: dataset/temporal_freq (e.g., "V5GL04/yearly")
    directory_label = f"{dataset_name}/{cfg.temporal_freq}"

    logger.info(f"Dataset: {dataset_name}")
    logger.info(f"Temporal frequency: {cfg.temporal_freq}")
    logger.info(f"Dataverse: {server_url}")
    logger.info(f"DOI: {doi}")
    logger.info(f"Target folder: {directory_label}")
    logger.info(f"Found {len(files_to_upload)} files to upload")

    # Check which files already exist on Dataverse
    logger.info("Checking existing files on Dataverse...")
    try:
        existing_files = check_existing_files(doi, server_url, api_token)
        logger.info(f"Found {len(existing_files)} files already on Dataverse")
    except Exception as e:
        logger.warning(f"Could not check existing files: {e}")
        existing_files = set()

    # Upload files
    uploaded = 0
    skipped = 0
    failed = 0

    for filepath in tqdm(files_to_upload, desc="Uploading"):
        filename = os.path.basename(filepath)

        # Check if file exists in the same directory
        if (directory_label, filename) in existing_files:
            logger.info(f"Skipping {filename} (already exists in {directory_label})")
            skipped += 1
            continue

        try:
            upload_file(filepath, doi, server_url, api_token, directory_label)
            uploaded += 1
            logger.info(f"Uploaded {filename}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload {filename}: {e}")
            failed += 1

    logger.info(f"Upload complete: {uploaded} uploaded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
