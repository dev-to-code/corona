import json
from pathlib import Path
from typing import Dict, List

base_dir = Path("data/CORD-19-research-challenge/2020-03-13")
biorxiv_medrxiv = base_dir.joinpath("biorxiv_medrxiv/biorxiv_medrxiv/")
comm_use_subset = base_dir.joinpath("comm_use_subset/comm_use_subset/")
pmc_custom_license = base_dir.joinpath("pmc_custom_license/pmc_custom_license/")
noncomm_use_subset = base_dir.joinpath("noncomm_use_subset/noncomm_use_subset/")
all_sources_metadata = base_dir.joinpath("all_sources_metadata_2020-03-13.csv")
all_dataset_sources = [
    biorxiv_medrxiv,
    comm_use_subset,
    pmc_custom_license,
    noncomm_use_subset,
]


class CovidPapers:

    def __init__(self, source_dir: str):
        self.source_path: str = None
        self.paper_index: Dict[str, int] = {}
        self.index_paper: Dict[int, str] = {}
        if isinstance(source_dir, str) or isinstance(source_dir, Path):
            source = Path(source_dir)
            if source.is_dir():
                source_files = [file for file in source.glob("*.json")]
                self._map_paper_ids(source_files)
                self.source_path = source
            else:
                raise ValueError(
                    "The path to directory is not valid" ", got {}.".format(source_dir)
                )

    @property
    def num_papers(self):
        return len(self.index_paper)

    @property
    def source_name(self):
        return self.source_path.parts[-1]

    def _map_paper_ids(self, json_files: List[str]):
        paper_index = {}
        for index, file in enumerate(json_files, start=1):
            paper_id = file.name.replace(".json", "")
            if paper_id not in paper_index:
                paper_index[paper_id] = index

        index_paper = {idx: pid for pid, idx in paper_index.items()}
        self.paper_index = paper_index
        self.index_paper = index_paper

    def _load_data(self, paper_id: str):
        file_path = self.source_path.joinpath(f"{paper_id}.json")
        with file_path.open("rb") as file:
            return json.load(file)

    def _encode(self, paper_ids: List[str]) -> List[int]:
        pid2idx = self.paper_index
        return [pid2idx[pid] for pid in paper_ids if pid in pid2idx]

    def _decode(self, indices: List[int]) -> List[str]:
        idx2pid = self.index_paper
        return [idx2pid[idx] for idx in indices if idx in idx2pid]

    def load_paper(self, index: int = None, paper_id: str = None):
        """Load a single paper and data by either index or paper-id."""
        if index is not None:
            paper = self.load_papers([index], None)
        elif paper_id is not None:
            paper = self.load_papers(None, [paper_id])
        return paper[0]

    def load_papers(self, indices: List[int] = None, paper_ids: List[str] = None):
        """Load many papers and data by either indices or paper-ids.

        NOTE: Sequences of items can loaded in any order.
        """
        if indices is not None:
            if isinstance(indices, list) and isinstance(indices[0], int):
                paper_ids = self._decode(indices)
                return [self._load_data(pid) for pid in paper_ids]
            else:
                raise ValueError("Indices not of type List[int].")

        elif paper_ids is not None:
            if isinstance(paper_ids, list) and isinstance(paper_ids[0], str):
                return [self._load_data(pid) for pid in paper_ids]
            else:
                raise ValueError("Paper ID not of type List[str].")

    def __repr__(self):
        return f"<COVID-19({self.source_name}, papers={self.num_papers})>"
