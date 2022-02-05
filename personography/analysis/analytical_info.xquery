declare namespace tei = "http://www.tei-c.org/ns/1.0";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method 'text';
declare variable $personography := doc('../methal-personography.xml');
declare variable $women := $personography//tei:person[descendant::tei:f[@name eq 'sex']/tei:symbol/@value eq 'F'];
declare variable $men := $personography//tei:person[descendant::tei:f[@name eq 'sex']/tei:symbol/@value eq 'M'];

declare function local:calculatePercentage($arg1 as node()+, $arg2 as node()+) as xs:string {
let $count1 := count($arg1)
let $count2 := count($arg2)
return ($count1 div $count2) => format-number('00.00%')
};

(:domestic workers by genre :)
let $domestic-workers-f := $women[descendant::tei:symbol/@value = 'domestic_worker']
let $domestic-workers-m := $men[descendant::tei:symbol/@value = 'domestic_worker']
let $domestic-total-f := local:calculatePercentage($domestic-workers-f, $women)
let $domestic-total-m := local:calculatePercentage($domestic-workers-m, $men)

(:characters with an occupation by genre and then filter domestic workers:)
let $prof-f := $women[descendant::tei:f/@name = 'occupation']
let $prof-m := $men[descendant::tei:f/@name = 'occupation']
let $prof-f_per := local:calculatePercentage($prof-f, $women)
let $prof-m_per := local:calculatePercentage($prof-m, $men)
let $prof-dom-f := local:calculatePercentage($prof-f[descendant::tei:symbol/@value = 'domestic_worker'], $prof-f)
let $prof-dom-m := local:calculatePercentage($prof-m[descendant::tei:symbol/@value = 'domestic_worker'], $prof-m)

(:characters with a family relation by genre:)
let $fam-f := local:calculatePercentage($women[descendant::tei:f/@name = 'family_position'], $women)
let $fam-m := local:calculatePercentage($men[descendant::tei:f/@name = 'family_position'], $men)

(:characters with either a family pr personal relation by genre:)
let $fam-pers-f := $women[descendant::tei:f/@name = ('family_position', 'personal_position')]
let $fam-pers-m := $men[descendant::tei:f/@name = ('family_position', 'personal_position')]
let $fam-pers-f_per := local:calculatePercentage($fam-pers-f, $women)
let $fam-pers-m_per := local:calculatePercentage($fam-pers-m, $men)

(:characters described exclusively with a family and/or a personal relation by genre:)
let $fam-excl-f := $fam-pers-f[not(descendant::tei:f/@name = 'occupation')]
let $fam-excl-m := $fam-pers-m[not(descendant::tei:f/@name = 'occupation')]
let $fam-excl-f_per := local:calculatePercentage($fam-excl-f, $women)
let $fam-excl-m_per := local:calculatePercentage($fam-excl-m, $men)

(:characters described exclusively with a occupation:)
let $prof-excl-f := $prof-f[not(descendant::tei:f/@name = ('family_position', 'personal_position'))]
let $prof-excl-m := $prof-m[not(descendant::tei:f/@name = ('family_position', 'personal_position'))]
let $prof-excl-f_per := local:calculatePercentage($prof-excl-f, $women)
let $prof-excl-m_per := local:calculatePercentage($prof-excl-m, $men)
let $dom-excl-f := local:calculatePercentage($prof-excl-f[descendant::tei:symbol/@value = 'domestic_worker'], $prof-excl-f)
let $dom-excl-m := local:calculatePercentage($prof-excl-m[descendant::tei:symbol/@value = 'domestic_worker'], $prof-excl-m)

return
    $domestic-total-f || ' of women are domestic workers but  ' || $prof-dom-f || 
    ' of women with an occupation are domestic workers&#10;' ||
    $domestic-total-m || ' of men are domestic workers but  ' || $prof-dom-m ||
    ' of men with an occupation are domestic workers&#10;&#10;' ||
    $fam-f || ' of women contain a family relation in their description (' || $fam-pers-f_per || 
    ' a family/personal relation) and ' || $prof-f_per || ' contain an occupation&#10;'
    || $fam-m || ' of men contain a family relation in their description (' || $fam-pers-m_per || 
    ' a family/personal relation) and ' || $prof-m_per || ' contain an occupation&#10;&#10;' ||
    $fam-excl-f_per || ' of women are described EXCLUSIVELY by a family and/or personal relation while this happens to '
    || $fam-excl-m_per || ' of men&#10;' || $prof-excl-f_per || ' of women are described EXCLUSIVELY with an occupation
    (and of those ' || $dom-excl-f || ' are domestic workers) and '
    || $prof-excl-m_per || ' of men (' || $dom-excl-m || ' being domestic workers)' 
    
