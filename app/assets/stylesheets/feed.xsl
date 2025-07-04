<?xml version="1.0"?>
<xsl:stylesheet
    version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:atom="http://www.w3.org/2005/Atom"
    exclude-result-prefixes="atom"
    >
    <xsl:output method="html" encoding="UTF-8" indent="yes" />
    <xsl:template match="/">
        <html class="govuk-template--rebranded">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
                <meta property="og:image" content="{atom:feed/atom:logo}"/>
                <meta property="og:title" content="{atom:feed/atom:title}"/>
                <title><xsl:value-of select="atom:feed/atom:title" /> Web Feed</title>
                <link rel="stylesheet" type="text/css" href="main.css"/>
                <link rel="icon" sizes="48x48"  href="{atom:feed/atom:icon}"/>
                <link rel="icon" sizes="any"  href="/alerts/assets/images/favicon-2ed10a55.svg" type="image/svg+xml"/>
            </head>
            <body class="govuk-template__body">
                <header class="govuk-header" role="banner">
                    <div class="govuk-header__container govuk-width-container">
                        <div class="govuk-header__logo">
                            <a class="govuk-header__link govuk-header__link--homepage">
                                <xsl:attribute name="href">
                                    <xsl:value-of select="substring-before(atom:feed/atom:link[@rel='alternate' and @type='application/html']/@href, '/alerts')" />
                                </xsl:attribute>
                                
                                <svg focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 324 60" height="30" width="162" class="govuk-header__logotype" aria-label="GOV.UK">
                                    <title>GOV.UK</title>
                                    <g>
                                        <circle cx="20" cy="17.6" r="3.7"></circle>
                                        <circle cx="10.2" cy="23.5" r="3.7"></circle>
                                        <circle cx="3.7" cy="33.2" r="3.7"></circle>
                                        <circle cx="31.7" cy="30.6" r="3.7"></circle>
                                        <circle cx="43.3" cy="17.6" r="3.7"></circle>
                                        <circle cx="53.2" cy="23.5" r="3.7"></circle>
                                        <circle cx="59.7" cy="33.2" r="3.7"></circle>
                                        <circle cx="31.7" cy="30.6" r="3.7"></circle>
                                        <path d="M33.1,9.8c.2-.1.3-.3.5-.5l4.6,2.4v-6.8l-4.6,1.5c-.1-.2-.3-.3-.5-.5l1.9-5.9h-6.7l1.9,5.9c-.2.1-.3.3-.5.5l-4.6-1.5v6.8l4.6-2.4c.1.2.3.3.5.5l-2.6,8c-.9,2.8,1.2,5.7,4.1,5.7h0c3,0,5.1-2.9,4.1-5.7l-2.6-8ZM37,37.9s-3.4,3.8-4.1,6.1c2.2,0,4.2-.5,6.4-2.8l-.7,8.5c-2-2.8-4.4-4.1-5.7-3.8.1,3.1.5,6.7,5.8,7.2,3.7.3,6.7-1.5,7-3.8.4-2.6-2-4.3-3.7-1.6-1.4-4.5,2.4-6.1,4.9-3.2-1.9-4.5-1.8-7.7,2.4-10.9,3,4,2.6,7.3-1.2,11.1,2.4-1.3,6.2,0,4,4.6-1.2-2.8-3.7-2.2-4.2.2-.3,1.7.7,3.7,3,4.2,1.9.3,4.7-.9,7-5.9-1.3,0-2.4.7-3.9,1.7l2.4-8c.6,2.3,1.4,3.7,2.2,4.5.6-1.6.5-2.8,0-5.3l5,1.8c-2.6,3.6-5.2,8.7-7.3,17.5-7.4-1.1-15.7-1.7-24.5-1.7h0c-8.8,0-17.1.6-24.5,1.7-2.1-8.9-4.7-13.9-7.3-17.5l5-1.8c-.5,2.5-.6,3.7,0,5.3.8-.8,1.6-2.3,2.2-4.5l2.4,8c-1.5-1-2.6-1.7-3.9-1.7,2.3,5,5.2,6.2,7,5.9,2.3-.4,3.3-2.4,3-4.2-.5-2.4-3-3.1-4.2-.2-2.2-4.6,1.6-6,4-4.6-3.7-3.7-4.2-7.1-1.2-11.1,4.2,3.2,4.3,6.4,2.4,10.9,2.5-2.8,6.3-1.3,4.9,3.2-1.8-2.7-4.1-1-3.7,1.6.3,2.3,3.3,4.1,7,3.8,5.4-.5,5.7-4.2,5.8-7.2-1.3-.2-3.7,1-5.7,3.8l-.7-8.5c2.2,2.3,4.2,2.7,6.4,2.8-.7-2.3-4.1-6.1-4.1-6.1h10.6,0Z"></path>
                                    </g>
                                    <circle class="govuk-logo-dot" cx="227" cy="36" r="7.3"></circle>
                                    <path d="M94.7,36.1c0,1.9.2,3.6.7,5.4.5,1.7,1.2,3.2,2.1,4.5.9,1.3,2.2,2.4,3.6,3.2,1.5.8,3.2,1.2,5.3,1.2s3.6-.3,4.9-.9c1.3-.6,2.3-1.4,3.1-2.3.8-.9,1.3-2,1.6-3,.3-1.1.5-2.1.5-3v-.4h-11v-6.6h19.5v24h-7.7v-5.4c-.5.8-1.2,1.6-2,2.3-.8.7-1.7,1.3-2.7,1.8-1,.5-2.1.9-3.3,1.2-1.2.3-2.5.4-3.8.4-3.2,0-6-.6-8.4-1.7-2.5-1.1-4.5-2.7-6.2-4.7-1.7-2-3-4.4-3.8-7.1-.9-2.7-1.3-5.6-1.3-8.7s.5-6,1.5-8.7,2.4-5.1,4.2-7.1c1.8-2,4-3.6,6.5-4.7s5.4-1.7,8.6-1.7,4,.2,5.9.7c1.8.5,3.5,1.1,5.1,2,1.5.9,2.9,1.9,4,3.2,1.2,1.2,2.1,2.6,2.8,4.1l-7.7,4.3c-.5-.9-1-1.8-1.6-2.6-.6-.8-1.3-1.5-2.2-2.1-.8-.6-1.7-1-2.8-1.4-1-.3-2.2-.5-3.5-.5-2,0-3.8.4-5.3,1.2s-2.7,1.9-3.6,3.2c-.9,1.3-1.7,2.8-2.1,4.6s-.7,3.5-.7,5.3v.3h0ZM152.9,13.7c3.2,0,6.1.6,8.7,1.7,2.6,1.2,4.7,2.7,6.5,4.7,1.8,2,3.1,4.4,4.1,7.1s1.4,5.6,1.4,8.7-.5,6-1.4,8.7c-.9,2.7-2.3,5.1-4.1,7.1s-4,3.6-6.5,4.7c-2.6,1.1-5.5,1.7-8.7,1.7s-6.1-.6-8.7-1.7c-2.6-1.1-4.7-2.7-6.5-4.7-1.8-2-3.1-4.4-4.1-7.1-.9-2.7-1.4-5.6-1.4-8.7s.5-6,1.4-8.7,2.3-5.1,4.1-7.1c1.8-2,4-3.6,6.5-4.7s5.4-1.7,8.7-1.7h0ZM152.9,50.4c1.9,0,3.6-.4,5-1.1,1.4-.7,2.7-1.7,3.6-3,1-1.3,1.7-2.8,2.2-4.5.5-1.7.8-3.6.8-5.7v-.2c0-2-.3-3.9-.8-5.7-.5-1.7-1.3-3.3-2.2-4.5-1-1.3-2.2-2.3-3.6-3-1.4-.7-3.1-1.1-5-1.1s-3.6.4-5,1.1c-1.5.7-2.7,1.7-3.6,3s-1.7,2.8-2.2,4.5c-.5,1.7-.8,3.6-.8,5.7v.2c0,2.1.3,4,.8,5.7.5,1.7,1.2,3.2,2.2,4.5,1,1.3,2.2,2.3,3.6,3,1.5.7,3.1,1.1,5,1.1ZM189.1,58l-12.3-44h9.8l8.4,32.9h.3l8.2-32.9h9.7l-12.3,44M262.9,50.4c1.3,0,2.5-.2,3.6-.6,1.1-.4,2-.9,2.8-1.7.8-.8,1.4-1.7,1.9-2.9.5-1.2.7-2.5.7-4.1V14h8.6v28.5c0,2.4-.4,4.6-1.3,6.6-.9,2-2.1,3.6-3.7,5-1.6,1.4-3.4,2.4-5.6,3.2-2.2.7-4.5,1.1-7.1,1.1s-4.9-.4-7.1-1.1c-2.2-.7-4-1.8-5.6-3.2s-2.8-3-3.7-5c-.9-2-1.3-4.1-1.3-6.6V14h8.7v27.2c0,1.6.2,2.9.7,4.1.5,1.2,1.1,2.1,1.9,2.9.8.8,1.7,1.3,2.8,1.7s2.3.6,3.6.6h0ZM288.5,14h8.7v19.1l15.5-19.1h10.8l-15.1,17.6,16.1,26.4h-10.2l-11.5-19.7-5.6,6.3v13.5h-8.7"></path>
                                    </svg>
                            </a>
                        </div>
                        <div class="govuk-header__content">
                            <span class="govuk-header__service-name">
                                <xsl:value-of select="atom:feed/atom:title" />
                            </span>
                        </div>
                    </div>
                </header>
                <div class="govuk-width-container">
                    <div class="govuk-grid-row govuk-subheader">
                        <div class="govuk-separator"></div>
                            <div class="govuk-language-select">
                                <nav class="govuk-body hmrc-language-select" aria-label="Language switcher">
                                    <ul class="hmrc-language-select__list">
                                    <li class="hmrc-language-select__list-item">
                                        <span aria-current="true">English</span>
                                    </li>
                                    <li class="hmrc-language-select__list-item">
                                        <a href="/alerts/feed_cy.atom" hreflang="cy" lang="cy" rel="alternate" class="govuk-link" data-journey-click="link - click:lang-select:Cymraeg">
                                        <span class="govuk-visually-hidden">Newid yr iaith ir Gymraeg</span>
                                        <span aria-hidden="true">Cymraeg</span>
                                        </a>
                                    </li>
                                    </ul>
                                </nav>
                            </div>
                    </div>
                    <main class="govuk-main-wrapper" role="main">
                        <xsl:apply-templates select="atom:feed" />
                        <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />
                        <h2 class="govuk-heading-m">Recent Alerts</h2>
                        <xsl:apply-templates select="atom:feed/atom:entry">
                            <xsl:sort select="atom:published" data-type="text()" order="descending"/>
                        </xsl:apply-templates>
                    </main>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="atom:feed">
        <h1 class="govuk-heading-xl">
            Emergency Alerts Web Feed
        </h1>
        <p class="govuk-body">
            This feed provides the latest posts from
            <a class="head_link" target="_blank">
                <xsl:attribute name="href">
                    <xsl:value-of select="atom:link[@rel='alternate' and @type='application/html']/@href" />
                </xsl:attribute>
                <xsl:value-of select="atom:subtitle" />
            </a>.
        </p>
        <div class="govuk-inset-text">
            <p class="govuk-body">
                Subscribe to this ATOM feed by copying the URL from the address bar into your feed reader app.
            </p>
        </div>
    </xsl:template>

    <xsl:template match="atom:entry">
        <h3 class="govuk-heading-m">
            <a target="_blank">
                <xsl:attribute name="href">
                    <xsl:value-of
                        select="atom:link/@href" />
                </xsl:attribute>
                <xsl:value-of select="atom:title" />
            </a>
        </h3>
        <p class="govuk-body atom-feed__word-wrap">
            <xsl:value-of select="atom:content" disable-output-escaping="yes" />
        </p>
        <p class="govuk-body-s">
            Published: <xsl:apply-templates select="atom:updated"/>
        </p>
        <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />
    </xsl:template>

    <xsl:template match="atom:updated">
        <xsl:variable name="datetime" select="normalize-space(.)"/>
        <xsl:variable name="date" select="substring-before($datetime, 'T')"/>
        <xsl:variable name="time" select="substring-after($datetime, 'T')"/>
        <xsl:value-of select="concat($date, ' ', substring($time, 1, 5))"/>
    </xsl:template>

</xsl:stylesheet>
