from pepsite.models import *
from .column_parsers import *
import pandas as pandas


class HeaderToDataFieldMappings:
    """Mapping of header column names (keys) to internal data field identifiers (values)"""
    ProteinPilotV5 = {
                "Accessions": "protein_uniprot_ids",
                     "Names": "protein_descriptions",
                      "Conf": "idestimate_confidence",
                  "Sequence": "peptide_sequence",
             "Modifications": "ptms_description",
                     "dMass": "ion_delta_mass",
                    "Obs MW": "idestimate_precursor_mass",
                   "Obs m/z": "ion_mz",
                   "Theor z": "ion_charge",
                  "Spectrum": "ion_spectrum",
                  "Acq Time": "ion_retention_time"
    }


class SpreadsheetToDataframe:

    def read_v5_csv(self, spreadsheet_filepath):
        """ Reads a ProteinPilot v5 spreadsheet and returns a Pandas DataFrame

        Uses Pandas' read_csv to parse the spreadsheet into a DataFrame for more efficient column/row operations.
        pandas.read_csv uses a dictionary of converters which applies functions to matching column names.
        These functions are defined in column_parsers.py. The functions also convert multiple-element cells to
        Python lists. Refer to spreadsheet specifications document for more information.

        :param spreadsheet_filepath: String with path to ProteinPilot V5 spreadsheet
        :return: Pandas DataFrame with column headers renamed to match internal data field identifiers
        """
        # "20160118_Amanda_QC6_QC6_01012016_afternewloadingpumpbuffer_PeptideSummary.txt"

        dataframe = pandas.read_csv(spreadsheet_filepath,
                                    usecols=HeaderToDataFieldMappings.ProteinPilotV5,
                                    delimiter='\t',
                                    converters={"Accessions": accessions_to_uniprot_list,
                                                "Names": names_to_protein_descriptions,
                                                "Modifications": modifications_to_ptms_descriptions})

        # Rename the column names to match models
        dataframe.rename(columns=HeaderToDataFieldMappings.ProteinPilotV5, inplace=True)

        return dataframe
