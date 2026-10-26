import cdsapi
from zipfile import ZipFile
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    
    client = cdsapi.Client()
    dataset = snakemake.config['dataset_id']
    request = {
        "variable": [
            "100m_u_component_of_wind",
            "100m_v_component_of_wind"
        ],
        "location": {"longitude": snakemake.config['longitude'], 
                     "latitude": snakemake.config['latitude']},
        "date": [snakemake.config['start_date']+"/"+snakemake.config['end_date']],
        "data_format": "csv",
    }
    target = snakemake.output.archive


    downloaded_file = client.retrieve(dataset, request, target)