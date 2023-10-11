[[français]](./README-fr.md)

# MeThAL : Towards a macroanalysis of theatre in Alsatian

Corpus creation, distant reading and historical sociolinguistics project, based on plays written in Alsatian varieties. Ongoing work carried out at the <a target="_blank" href="http://lilpa.unistra.fr/">LiLPa</a> lab. This repository contains plays encoded in TEI by the project and other resources about the collection. The repo is updated as encoding progresses.

- Project site: <a target="_blank" href="https://methal.pages.unistra.fr">https://methal.pages.unistra.fr/en.html</a>
- Corpus exploration interface: <a target="_blank" href="https://methal.eu/ui/">https://methal.eu/ui/</a>
- Permanent (DOI-based) publication of the TEI-encoded resources is done through a <a target="_blank" href="https://nakala.fr/collection/10.34847/nkl.feb4r8j9">collection</a> at the Nakala platform
  - Besides the plays already assigned a DOI, a pre-release version of several plays, that can already be used for analyses, can found at [tei-pre-release](./tei-pre-release) in this repository


## Repository content

- The **TEI-encoded plays**. These are found in two directories:
  - [[tei]](./tei): These plays have been assigned a DOI via the Nakala repository. As an [overview](#plays-available-in-tei), these plays are listed in the table [below](#plays-available-in-tei)
  - [[tei-pre-release]](./tei-pre-release): These plays have been subjected to less verifications than the ones in the `tei` directory and a DOI has not yet been assigned. They have however already been used for several studies (e.g. <a target="_blank" href="https://doi.org/10.5281/zenodo.8404252">emotion analysis</a>)
- A [**TEI personography**](./personography) for a larger set of plays is also available. It describes over 2,350 characters in ca. 230 plays. Character social variables (age, sex, professional group, social class) are annotated
- A <a target="_blank" href="https://git.unistra.fr/methal/methal-sources/-/wikis/home">wiki</a> documents our encoding practices
- Software we developed for encoding can be found at [encoding-workflow](./encoding-workflow)

Besides this repository, an <a target="_blank" href="https://methal.eu/ui/">online interface</a> gives access to the text for all plays and their metadata

## Participants

Pablo Ruiz (project lead), Delphine Bernhard, Pascale Erhart, Dominique Huck, Carole Werner, at the LiLPa lab.

Special mention to the many interns that we've been fortunate to work with: Nathanaël Beiner, Lena Camillone, Hoda Chouaib, Audrey Deck, Valentine Jung, Salomé Klein, Audrey Li-Thiao-Te, Kévin Michoud, Alexia Schneider and Vedisha Toory among University of Strasbourg students. From other schools, Andrew Briand (University of Washington via IFE Strasbourg), Barbara Hoff (University of Edinburgh), Qinyue Liu and Heng Yang (Université Grenoble Alpes).

## Plays published with a DOI via the Nakala repository

(Further TEI plays, not yet released via Nakala, can be found at the [tei-pre-release](./tei-pre-release) directory)

|Author|First<br>Printed|Our<br>Source|Title<br>(DOI)|Subtitle|Genre|TEI source|
|---|---|---|---|---|---|---|
|Johann Georg Daniel Arnold|1816|1914|Der Pfingstmontag<br><a href='https://doi.org/10.34847/nkl.b37bfx3q'>(10.34847/nkl.b37bfx3q)</a>|Lustspiel in Straßburger Mundart. Nach der vom Dichter durchgesehenen zweiten Ausgabe des Jahres 1816 herausgegeben von J. Lefftz und E. Marckwald|comedy|[[tei]](./tei/arnold-der-pfingstmontag.xml)|
|Ferdinand Bastian|1903|1930|D'r Hans im Schnokeloch<br><a href='https://doi.org/10.34847/nkl.7a84q6be'>(10.34847/nkl.7a84q6be)</a>|Volksspiel in 4 Aufzügen mit Musik, Gesang und Tanz von Ferd. Bastian|comedy|[[tei]](./tei/bastian-dr-hans-im-schnokeloch.xml)|
|Ferdinand Bastian|1937|1937|D'r Maischter hett gewunne!<br><a href='https://doi.org/10.34847/nkl.6a64e71a'>(10.34847/nkl.6a64e71a)</a>|Schwank in aam Akt|comedy|[[tei]](./tei/bastian-dr-maischter-hett-gewunne.xml)|
|Ferdinand Bastian|1937|1937|D’r Hofnarr Heidideldum<br><a href='https://doi.org/10.34847/nkl.da2cn58f'>(10.34847/nkl.da2cn58f)</a>|Märel in 6 Bilder un 2 Verwandlunge vun Ferd. Bastian. Musik von Aug. Schwoob|tale|[[tei]](./tei/bastian-hofnarr-heidideldum.xml)|
|Ferdinand Bastian|1937|1937|E Sportshochzitt<br><a href='https://doi.org/10.34847/nkl.116e0h03'>(10.34847/nkl.116e0h03)</a>|E Farce in aam Akt|comedy|[[tei]](./tei/bastian-e-sportshochzitt.xml)|
|Paul Clemens|1920|1920|A lätzi Visit<br><a href='https://doi.org/10.34847/nkl.3ff34nzm'>(10.34847/nkl.3ff34nzm)</a>|Elsässisch Luschtspiel in 1 Akt vun Paul Clemens|comedy|[[tei]](./tei/clemens-a-latzi-visit.xml)|
|Paul Clemens|1919|1919|Chrischtowe<br><a href='https://doi.org/10.34847/nkl.09e9vq3m'>(10.34847/nkl.09e9vq3m)</a>|E Wihnachtsstüeckel in 1 Akt in elsässischem Dialekt füer kleine und grossi Kinder|tale|[[tei]](./tei/clemens-chrischtowe.xml)|
|Paul Clemens|1920|1920|D' Brueder<br><a href='https://doi.org/10.34847/nkl.cbbfc28w'>(10.34847/nkl.cbbfc28w)</a>|Volksstück in 5 Bilder üs dr Zitt vun 1914 bis 1918<br>vun Paul Clemens, Membre du Théâtre Alsacien|volksstück|[[tei]](./tei/clemens-d-brueder.xml)|
|Paul Clemens|1920|1920|D'r Amerikaner<br><a href='https://doi.org/10.34847/nkl.6ce9m29w'>(10.34847/nkl.6ce9m29w)</a>|Elsässisches Volksstück in 3 Aufzügen von Paul Clemens, Membre du Théâtre Alsacien|comedy|[[tei]](./tei/clemens-dr-amerikaner.xml)|
|Paul Clemens|1919|1919|Gift!<br><a href='https://doi.org/10.34847/nkl.0dc51j2m'>(10.34847/nkl.0dc51j2m)</a>|Schwank in einem Akt in elsässischer Mundart|comedy|[[tei]](./tei/clemens-gift.xml)|
|Paul Clemens|1920|1920|„Charlot“<br><a href='https://doi.org/10.34847/nkl.e2f80kzi'>(10.34847/nkl.e2f80kzi)</a>|E ürgelungenes Stückel in 1 Akt im elsässischa Dialekt von Paul Clemens, Bischheim (Nur Herrenrollen)|comedy|[[tei]](./tei/clemens-charlot.xml)|
|Ernst Fuchs|1914|1914|Heimlichi Lieb<br><a href='https://doi.org/10.34847/nkl.670a8898'>(10.34847/nkl.670a8898)</a>|Elsässisch's Volksstüeck in 7 Bilder|drama|[[tei]](./tei/fuchs-heimlichi-lieb.xml)|
|Julius Greber|1910|1910|'s Teschtament<br><a href='https://doi.org/10.34847/nkl.092b0a3k'>(10.34847/nkl.092b0a3k)</a>|Volksstück in drei Aufzügen von Julius Greber|volksstück|[[tei]](./tei/greber-s-teschtament.xml)|
|Julius Greber|1899|1899|D'Jumpfer Prinzesse<br><a href='https://doi.org/10.34847/nkl.e9ca8n72'>(10.34847/nkl.e9ca8n72)</a>|Schauspiel in 3 Aufzügen in Straßburger Mundart von Julius Greber. Mit einer Deckenzeichnung von C. Spindler.|drama|[[tei]](./tei/greber-d-jumpfer-prinzesse.xml)|
|Julius Greber|1896|1896|Lucie<br><a href='https://doi.org/10.34847/nkl.d0ce03vx'>(10.34847/nkl.d0ce03vx)</a>|Dramatisches Sittenbild in einem Aufzuge in Straßburger Mundart|drama|[[tei]](./tei/greber-lucie.xml)|
|Julius Greber|1897|1897|Sainte-Cécile!<br><a href='https://doi.org/10.34847/nkl.954534jw'>(10.34847/nkl.954534jw)</a>|Lustspiel in einem Aufzuge in Straßburger Mundart von Julius Greber|comedy|[[tei]](./tei/greber-sainte-cecile.xml)|
|Hermann Günther|1907|1907|D'r Cousin Réfractaire<br><a href='https://doi.org/10.34847/nkl.9834lzo3'>(10.34847/nkl.9834lzo3)</a>|E Stroßburjer Familiefarce in 2 Akte|comedy|[[tei]](./tei/gunther-dr-cousin-refractaire.xml)|
|Emilie Hahn|1922|1922|Jungi Madamme<br><a href='https://doi.org/10.34847/nkl.dd7e4580'>(10.34847/nkl.dd7e4580)</a>|Lustspiel in einem Aufzug in Strassburger Mundart|comedy|[[tei]](./tei/hahn-jungi-madamme.xml)|
|Marie Hart|1937|1937|D'r poetisch Oscar<br><a href='https://doi.org/10.34847/nkl.9f28120s'>(10.34847/nkl.9f28120s)</a>|einakter|comedy|[[tei]](./tei/hart-dr-poetisch-oscar.xml)|
|Adolphe Horsch|1901|1901|D'Madam fahrt Velo<br><a href='https://doi.org/10.34847/nkl.73963p3s'>(10.34847/nkl.73963p3s)</a>|E modern's Lustspiel in 1 Akt|comedy|[[tei]](./tei/horsch-d-madam-fahrt-velo.xml)|
|Adolphe Horsch|1908|1908|Neui Hosse<br><a href='https://doi.org/10.34847/nkl.d4e6plk5'>(10.34847/nkl.d4e6plk5)</a>|Comédie-Bouffe in eim Akt von D. G. Ad. Horsch|comedy|[[tei]](./tei/horsch-neui-hosse.xml)|
|Camille Jost|1928|1928|E Daa im Narrehüss<br><a href='https://doi.org/10.34847/nkl.eeb0p8dq'>(10.34847/nkl.eeb0p8dq)</a>|E Original-Farce in zwei kurze  Akt vum Camille Jost|comedy|[[tei]](./tei/jost-daa-im-narrehuss.xml)|
|Camille Jost|1928|1928|So e liederlicher Frack!<br><a href='https://doi.org/10.34847/nkl.c11eu48d'>(10.34847/nkl.c11eu48d)</a>|odder:E foljieschwäri Hüssuechung. E Schwank in 1 Uffzug|comedy|[[tei]](./tei/jost-so-e-liederlicher-frack.xml)|
|Charles Frédéric Kettner|1924|1924|Uff Dr Hochzittsreis<br><a href='https://doi.org/10.34847/nkl.ce4e3x5m'>(10.34847/nkl.ce4e3x5m)</a>|Luschtspiel in 1 Akt im els. Dialekt|comedy|[[tei]](./tei/kettner-uff-dr-hochzittsreis.xml)|
|H. Kleisecker|1920|1920|D'r Schnider von Gambse<br><a href='https://doi.org/10.34847/nkl.6eac7s0o'>(10.34847/nkl.6eac7s0o)</a>|Lustspiel von H. Kleisecker|comedy|[[tei]](./tei/kleisecker-dr-schnider-von-gambse.xml)|
|Fernand Kuehne|1923|1923|Bureaukrate!<br><a href='https://doi.org/10.34847/nkl.e835319f'>(10.34847/nkl.e835319f)</a>|Dialektkomödie in einem Akt|comedy|[[tei]](./tei/kuehne-bureaukrate.xml)|
|Jean Riff|1919|1919|Sainte Barbe<br><a href='https://doi.org/10.34847/nkl.89ddf957'>(10.34847/nkl.89ddf957)</a>|Comédie in Aam Uffzug vun Jean Riff|comedy|[[tei]](./tei/riff-sainte-barbe.xml)|
|Jean Riff|1922|1922|s' Paradies<br><a href='https://doi.org/10.34847/nkl.fe9227bq'>(10.34847/nkl.fe9227bq)</a>|E luschdigs Schwänkele in aam Uffzug von Jean Riff|comedy|[[tei]](./tei/riff-s-paradies.xml)|
|Heinrich Schneegans|1897|1897|Was d' Steckelburjer vun d'r „Université“ saaue<br><a href='https://doi.org/10.34847/nkl.041dsnu6'>(10.34847/nkl.041dsnu6)</a>|Humoristisches Intermezzo von Dr. Heinrich Schneegans Privatdocent, Aufgeführt zum Universitäts-Jubiläum am 2. Mai 1897|comedy|[[tei]](./tei/schneegans-steckelburjer-universite-saaue.xml)|
|Xavier Sengelin|1920|1920|D'Mamsell Elis<br><a href='https://doi.org/10.34847/nkl.ae2ej4j5'>(10.34847/nkl.ae2ej4j5)</a>|Volksstück üsm Bürelawe in 3 Akte un 1 Vorakt|volksstück|[[tei]](./tei/sengelin-d-mamsell-elis.xml)|
|Gustave Stoskopf|1898|1935|D'r Herr Maire<br><a href='https://doi.org/10.34847/nkl.a33ckqpb'>(10.34847/nkl.a33ckqpb)</a>|Lustspiel in drei Aufzügen von G. Stoskopf|comedy|[[tei]](./tei/stoskopf-dr-herr-maire.xml)|
|Gustave Stoskopf|1906|1906|D'r Hoflieferant<br><a href='https://doi.org/10.34847/nkl.fb0171s7'>(10.34847/nkl.fb0171s7)</a>|Elsassiche Komödie in 3 Aufzügen von G. Stoskopf|comedy|[[tei]](./tei/stoskopf-dr-hoflieferant.xml)|
|Gustave Stoskopf|1899|1906|E Diplomat<br><a href='https://doi.org/10.34847/nkl.3a89d070'>(10.34847/nkl.3a89d070)</a>|Zwei Lustpiele in Strassburger Mundart von G. Stoskopf. Mit 7 Illustrationen von P. Braunagel|comedy|[[tei]](./tei/stoskopf-e-diplomat.xml)|
|Gustave Stoskopf|1907|1907|In's Ropfer's Apothek<br><a href='https://doi.org/10.34847/nkl.b5fctsyx'>(10.34847/nkl.b5fctsyx)</a>|Schwank in 3 Aufzügen von G. Stoskopf|comedy|[[tei]](./tei/stoskopf-ins-ropfers-apothek.xml)|
|Emile Weber|1936|1936|E bissel Lieb<br><a href='https://doi.org/10.34847/nkl.ae77r3q4'>(10.34847/nkl.ae77r3q4)</a>|Drama im e Vorspiel un 3 Akt von Emile Weber, 5 Herren - 3 Damen|drama|[[tei]](./tei/weber-e-bissel-lieb.xml)|
|Emile Weber|1932|1932|Yo-Yo!<br><a href='https://doi.org/10.34847/nkl.caddeub3'>(10.34847/nkl.caddeub3)</a>|E Geduldspiel in einem Akt|comedy|[[tei]](./tei/weber-yo-yo.xml)|


## License

- [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
