# Snakefile for PM2.5 Box → Dataverse pipeline
#
# Usage:
#   snakemake --cores 1              # Run all downloads and uploads
#   snakemake --cores 1 -n           # Dry run (show what would run)
#   snakemake --cores 1 download_all # Only download, no upload
#
# To run a specific dataset/frequency:
#   snakemake --cores 1 data/V5GL04/yearly/.uploaded

DATASETS = ["V5GL04", "V5GL0502", "V6GL02"]
TEMPORAL = ["yearly", "monthly"]

rule all:
    input:
        expand("data/{dataset}/{temporal}/.uploaded", dataset=DATASETS, temporal=TEMPORAL)

rule download_all:
    input:
        expand("data/{dataset}/{temporal}/.downloaded", dataset=DATASETS, temporal=TEMPORAL)

rule download:
    output:
        marker = "data/{dataset}/{temporal}/.downloaded"
    log:
        "logs/download_{dataset}_{temporal}.log"
    shell:
        """
        python src/download_from_box.py datasets={wildcards.dataset} temporal_freq={wildcards.temporal} 2>&1 | tee {log}
        touch {output.marker}
        """

rule upload:
    input:
        "data/{dataset}/{temporal}/.downloaded"
    output:
        marker = "data/{dataset}/{temporal}/.uploaded"
    log:
        "logs/upload_{dataset}_{temporal}.log"
    shell:
        """
        python src/upload_to_dataverse.py datasets={wildcards.dataset} temporal_freq={wildcards.temporal} 2>&1 | tee {log}
        touch {output.marker}
        """
