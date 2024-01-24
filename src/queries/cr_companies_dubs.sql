WITH
	"shows" AS (
		SELECT cr.season, cr.year, COUNT(*) AS num, SUM(dub) AS dubs
		FROM cr
		GROUP BY cr.year, cr.season
	),
	"company_all" AS (
		SELECT COUNT(DISTINCT(ca.anime_id)) AS num, cr.season, cr.year
		FROM cr
		INNER JOIN company_anime ca ON cr.myanimelist = ca.anime_id
		INNER JOIN company c ON ca.company_id = c.company_id
		INNER JOIN anime a ON cr.myanimelist = a.anime_id
		WHERE c.name IN ({qm})
		GROUP BY cr.year, cr.season
	),
	"company_dubs" AS (
		SELECT COUNT(DISTINCT(ca.anime_id)) AS dubs, cr.season, cr.year
		FROM cr
		INNER JOIN company_anime ca ON cr.myanimelist = ca.anime_id
		INNER JOIN company c ON ca.company_id = c.company_id
		INNER JOIN anime a ON cr.myanimelist = a.anime_id
		WHERE c.name IN ({qm})
		AND cr.dub = 1
		GROUP BY cr.year, cr.season
	)
SELECT s.season, s.year, s.num AS "total", s.dubs AS "total dubs", ca.num, cd.dubs, ROUND(100.0 * cd.dubs / ca.num, 2) || "%" AS "pct dubbed", ROUND(100.0 * cd.dubs / s.dubs, 2) || "%" AS "pct of dubs"
FROM shows s
INNER JOIN company_all ca ON (s.season = ca.season AND s.year = ca.year)
INNER JOIN company_dubs cd ON (s.season = cd.season AND s.year = cd.year)
ORDER BY s.year DESC, s.season = "winter", s.season = "spring", s.season = "summer", s.season = "fall"
