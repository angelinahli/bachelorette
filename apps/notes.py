import dash_core_components as dcc
import dash_html_components as html

import utils
from app import app

title = "Notes"
subtitle = "Data & Methodology"

urls = dict(
  census_url="https://factfinder.census.gov/faces/affhelp/jsf/pages/" \
    + "metadata.xhtml?lang=en&type=table&id=table.en.ACS_16_1YR_B03002",
  karenx_url="http://www.karenx.com/blog/minorities-on-the-bachelor-when-do-" \
    + "they-get-eliminated/",
  five38_url="https://github.com/fivethirtyeight/data/tree/master/bachelorette",
  ba_wiki_url="https://en.wikipedia.org/wiki/The_Bachelor_(U.S._TV_series)",
  be_wiki_url="https://en.wikipedia.org/wiki/The_Bachelorette",
  race_source_url="https://github.com/angelinahli/bachelorette/blob/master/" \
    + "data/input/poc_categorization.xlsx",
  race_justif_url="https://github.com/angelinahli/bachelorette/tree/master/" \
    + "data/input/race",
  scripts_url="https://github.com/angelinahli/bachelorette/tree/master/" \
    + "data/scripts"
)

main_content = dcc.Markdown(
  """
  #### Data Sources
  
  ##### Contestants
  * [538]({five38_url}) data
  * Supplemental data for Season 22 of the Bachelor and Season 14 of the 
    Bachelorette from Wikipedia
  
  ##### Race
  * [karenx]({karenx_url})'s dataset
  * [US Census]({census_url}) 'Hispanic or Latino Origin by Race' 
    ACS 1-year variable
  * Individual sources listed for person-level race data

  ##### Seasons
  * [Bachelor]({ba_wiki_url}) and [Bachelorette]({be_wiki_url}) Wikipedia pages
  
  ---

  #### Methodology

  ##### General
  * This application relies upon individual level data on Bachelor and
    Bachelorette U.S. seasons from 2002 - 2018.
  * Bachelor/ette seasons are included in this application if I was able to find
    individual level race data on all cast members of that season. For practical
    purposes, this excluded several early seasons of the franchise.
  * All the Jupyter Notebooks used to clean the data used in this project
    can be [found on Github]({scripts_url}).

  ##### Race Data
  * For the purposes of this investigation, I hand-labelled cast members based
    on their perceived racial / ethnic identities. My methodology was as follows:
    * If I found a statement from the cast member vouching for their own racial 
      / ethnic identity, I deferred to what the cast member said of their own 
      identity.
    * Otherwise, if I found a third party assessment of the cast member's
      ethnic identity (e.g. from formal and informal news accounts), I
      deferred to that third party assessment.
    * Otherwise, if there was a published photo of the cast member, I would use 
      that photo to determine the cast members' perceived ethnic / racial 
      identity.
  * A full list of sources I relied upon to verify Bachelor/ette cast members'
    racial / ethnic identities can be [found on Github]({race_source_url}).
  * A further discussion of this methodology can be [found here](
    {race_justif_url}).
  """.format(**urls)
)

layout = utils.BSContainer(
  title=title,
  subtitle=subtitle,
  main_content=main_content)
