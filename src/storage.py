import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        self._counter += 1
        id = self._counter
        df_copy = df.copy()
        self._store[id] = [filename, df_copy]
        logger.debug(f"Saved dataset with ID {id} and filename {filename}")
        return id


    def get(self, dataset_id):
        if dataset_id in self._store:
            logger.debug(f"Retrieved dataset with ID {dataset_id}")
            return self._store[dataset_id][1].copy()
        return None


    def get_metadata(self, dataset_id):
        if dataset_id in self._store:
            file = self._store[dataset_id][0] 
            df = self._store[dataset_id][1]
            rows = len(df)
            columns = len(df.columns)
            column_names = list(df.columns)
            logger.debug(f"Retrieved metadata for dataset with ID {dataset_id}")
            return dataset_id, file, rows, columns, column_names
        return None
        

    def update(self, dataset_id, df):
        if dataset_id in self._store:
            self._store[dataset_id][1] = df.copy()
            logger.debug(f"Updated dataset with ID {dataset_id}")
            return True
        logger.debug(f"Dataset with ID {dataset_id} not found for update")
        return False
            

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
        logger.debug("Cleared all datasets and reset ID counter")
