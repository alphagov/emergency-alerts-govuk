<?xml version="1.0"?>
<xsl:stylesheet
    version="2.0"
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
                <title><xsl:value-of select="atom:feed/atom:title" /> Web Feed</title>
                <link rel="stylesheet" type="text/css" href="/alerts/assets/stylesheets/main-2aabca4b.css"/>
            </head>
            <body>
                <section>
                    <div class="govuk-inset-text">
                        <p>
                            Subscribe to this ATOM feed by copying the URL from the address bar into your
                            feed reader app. Share this feed with your Slack team by messaging:
                            <code>
                                /feed subscribe <xsl:value-of select="atom:feed/atom:link[@rel='self']/@href" />
                            </code>
                        </p>
                    </div>
                </section>
                <section>
                    <xsl:apply-templates select="atom:feed" />
                </section>
                <section>
                    <h2>Recent Items</h2>
                    <xsl:apply-templates select="atom:feed/atom:entry" />
                </section>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="atom:feed">
        <div class="feed-logo">
            <img class="feed-logo">
                <xsl:attribute name="src">
                    <xsl:value-of select="atom:icon" />
                </xsl:attribute>
            </img>
        </div>
        <h1>
            <xsl:value-of select="atom:title" /> Web Feed Preview
        </h1>
        <p>
            This feed provides the latest posts from <xsl:value-of select="atom:title" />.
            <a class="head_link" target="_blank">
                <xsl:attribute name="href">
                    <xsl:value-of select="atom:link[@rel='alternate' and @type='application/html']/@href" />
                </xsl:attribute>
                Visit Website &#x2192;
            </a>
        </p>
    </xsl:template>
    <xsl:template match="atom:entry">
        <div class="entry">
            <h3>
                <a target="_blank">
                    <xsl:attribute name="href">
                        <xsl:value-of
                            select="atom:link/@href" />
                    </xsl:attribute>
                    <xsl:value-of select="atom:title" />
                </a>
            </h3>
            <p>
                <xsl:value-of select="atom:summary" disable-output-escaping="yes" />
            </p>
            <small> Published: <xsl:value-of select="atom:updated" />
            </small>
        </div>
    </xsl:template>
</xsl:stylesheet>
