<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0" version="3.0">

    <!-- xpath-default-namespace for input -->
    <!--
        xmlns for output, actually anything without a prefix is this
        if want to use other elements from other namespaces you need
        to declare each namespace and then a prefix is useful
        
        xsl and xs as prefixes are just so that you can write xsl and
        xml schema elements, instructions etc
    -->
    <!-- /home/ruizfabo/te/stra/re/theatre_alsacien/ressources/ropfer/Ropfer Stoskopf -->

    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>

    <!-- Run from Oxygen XSLT view, choose any file in the input folder as input -->

    <xsl:variable name="docs" select="collection('RopferStoskopf_hOCR')//html"/>

    <xsl:template match="/">
        <xsl:result-document href="RopferStoskopfTEI/stoskopf-ropfer.xml">
            <TEI>
                <teiHeader>
                    <fileDesc>
                        <titleStmt>
                            <title>Title</title>
                        </titleStmt>
                        <publicationStmt>
                            <p>Publication information</p>
                        </publicationStmt>
                        <sourceDesc>
                            <p>Information about the source</p>
                        </sourceDesc>
                    </fileDesc>
                </teiHeader>
                <text>
                    <body>
                        <p>Some text here.</p>
                        <figure>
                            <graphic url="http://www.tei-c.org/logos/TEI-glow.png"/>
                        </figure>
                        <xsl:apply-templates select="$docs">
                            <xsl:sort select="//head/title"/>
                        </xsl:apply-templates>
                    </body>
                </text>
            </TEI>
        </xsl:result-document>

    </xsl:template>

    <xsl:template match="html">
        <xsl:variable name="pb">
            <!-- give output of substring-before as input to substring-after -->
            <xsl:value-of select="substring-after(head/title/substring-before(., '.'), '-')"/>
        </xsl:variable>
        <pb n="{number($pb)-4}"/>
        <xsl:apply-templates select="body"/>
    </xsl:template>
    <!-- ignore text in nodes that do not match the filter -->
    <xsl:template match="div">
        <xsl:apply-templates
            select="
                //p[not(descendant::span[matches(., '[^A-Za-z][—-][^A-Za-z]')]/following-sibling::span[matches(., '\d+')])]
                [not(descendant::span[matches(., '^\s*[—-]\s+\d+\s+[—-]\s*$')])]"
        />
        <!--<xsl:apply-templates
            select="
                //p[not(descendant::span[matches(., '[—-][A-Za-z]')]/following-sibling::span[matches(., '\d+')])][not(descendant::span[matches(., '[—-]')]/following-sibling::span[matches(., '\d+')])]
                [not(descendant::span[matches(., '^\s*[—-]\s+\d+\s+[—-]\s*$')])]"
        />-->
    </xsl:template>
    <xsl:template match="p">
        <xsl:choose>
            <xsl:when test="descendant::strong[contains(., 'Aufzug')]">
                <head>
                    <xsl:value-of select="."/>
                </head>
            </xsl:when>
            <xsl:when test="not(descendant::strong)">
                <stage>
                    <xsl:apply-templates/>
                </stage>
            </xsl:when>
            <xsl:otherwise>
                <sp>
                    <xsl:apply-templates/>
                   <!-- <xsl:variable name="speaker" select="string-join(descendant::strong, ' ')"/>
                   <speaker><xsl:value-of select="$speaker"/></speaker>
                    <xsl:value-of select="descendant::span[not(descendant::strong)]"></xsl:value-of>
             -->   </sp>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
<xsl:template match="strong[not(parent::span/preceding-sibling::span/strong)]">
    <speaker><xsl:apply-templates/>
    <xsl:if test="parent::span/following-sibling::span/strong">
        <xsl:text> </xsl:text>
        <xsl:value-of select="parent::span/following-sibling::span/strong"/>
    </xsl:if></speaker>
</xsl:template>
    <xsl:template match="strong[parent::span/preceding-sibling::span/strong]"/>
</xsl:stylesheet>
