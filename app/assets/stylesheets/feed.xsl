<?xml version="1.0"?>
<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:atom="http://www.w3.org/2005/Atom"
    exclude-result-prefixes="atom"
    >
    <xsl:output method="html" encoding="UTF-8" indent="yes" />
    <xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
                <title>Web Feed • <xsl:value-of select="atom:feed/atom:title" /></title>
                <style type="text/css">
                    body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                    }
                    .container {
                    width: 80%;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1, h2, h3 {
                    color: #333;
                    }
                    .entry {
                    border-bottom: 1px solid #ddd;
                    padding: 10px 0;
                    }
                    .entry:last-child {
                    border-bottom: none;
                    }
                    .entry h3 {
                    margin: 0;
                    }
                    .entry p {
                    margin: 5px 0;
                    }
                    .entry small {
                    color: #666;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>
                        <xsl:value-of select="atom:feed/atom:title" />
                    </h1>
                    <p>
                        <xsl:value-of select="atom:feed/atom:subtitle" />
                    </p>
                    <xsl:apply-templates select="atom:feed/atom:entry" />
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="atom:entry">
        <div class="entry">
            <h3>
                <a target="_blank">
                    <xsl:attribute name="href">
                        <xsl:value-of select="atom:link[@rel='alternate']/@href" />
                    </xsl:attribute>
                    <xsl:value-of select="atom:title" />
                </a>
            </h3>
            <p>
                <xsl:value-of select="atom:summary" disable-output-escaping="yes" />
            </p>
            <small>Published: <xsl:value-of select="atom:updated" /></small>
        </div>
    </xsl:template>
</xsl:stylesheet>
