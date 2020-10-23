#coding=utf8

"""
To add person description to <front> element of E Daa im Narrehüs TEI
"""

from lxml import etree
import pandas as pd
import re
import sys

sys.path.append("../..")

import config as cf
import utils.utils as ut


def extract_character_description_from_df(dfpath=cf.cast_list_data):
    """
    Prepare character description to write TEI page, based on dataframe
    information (columns _otherDesc_ and _persName_)

    Parameters
    ----------
    dfpath : str, optional
        Path to ODS sheet with information to create dataframe.
        Default value is in :obj:`config` module (`cf.cast_list_data`)

    Returns
    -------
    pandas.DataFrame
        Dataframe with information to write out.
    """
    df = ut.read_character_info(dfpath)
    df['persName'] = df['persName'].apply(lambda x: re.sub("^Dr\.?\s*", "", x))
    df_name_des = df.loc[pd.notnull(df.otherDesc), ['persName', 'otherDesc']]
    return df_name_des


def create_character_description_page(df):
    """

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    lxml.etree.Element
        A `<div>` element containing a TEI <list> element
        with the character description
    """
    div = etree.Element("div", type="character-description")
    list = etree.SubElement(div, "list", rend="numbered")
    etree.SubElement(list, "head").text = "Rolle-Beschrywung:"
    for idx, row in df.iterrows():
        # adding a tail (would be ';' here) not allowed in TEI schema
        etree.SubElement(list, "label").text = row.persName
        etree.SubElement(list, "item").text = row.otherDesc
    return div


def add_character_description_to_front(
        fr, dfpath=cf.cast_list_data, pnbr=cf.character_description_pnbr):
    """
    Append a div with a character description list to the front element
    of a TEI file.

    Parameters
    ----------
    fr : lxml.etree.Element
        TEI <front> element to append to
    dfpath : str, optional
        Path to ODS sheet with information to create dataframe with
        character information.
        Default value is in :obj:`config` module (`cf.cast_list_data`)
    pnbr : int, optional
        Page number for the `<pb>` element to insert before the description

    Returns
    -------
    None
    """
    fr.append(etree.fromstring(f"<pb n='{pnbr}'/>"))
    cd = extract_character_description_from_df(dfpath)
    div =  create_character_description_page(cd)
    fr.append(div)


if __name__ == "__main__":
    dd = extract_character_description_from_df()
    div = create_character_description_page(dd)
