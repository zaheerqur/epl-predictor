export const COLORS = {
  'Arsenal':           ['#EF0107','#fff'],   'Aston Villa':     ['#670E36','#95BFE5'],
  'Bournemouth':       ['#B50E12','#fff'],   'Brentford':       ['#E30613','#fff'],
  'Brighton':          ['#0057B8','#fff'],   'Burnley':         ['#6C1D45','#99D6EA'],
  'Chelsea':           ['#034694','#fff'],   'Crystal Palace':  ['#1B458F','#C4122E'],
  'Everton':           ['#003399','#fff'],   'Fulham':          ['#CC0000','#fff'],
  'Ipswich':           ['#0044A9','#fff'],   'Leeds':           ['#1D428A','#FFCD00'],
  'Leicester':         ['#003090','#FDBE11'],'Liverpool':       ['#C8102E','#F6EB61'],
  'Luton':             ['#F78F1E','#231F20'],'Man City':        ['#6CABDD','#1C2C5B'],
  'Man United':        ['#DA291C','#FBE122'],'Middlesbrough':   ['#E01B22','#fff'],
  'Newcastle':         ['#241F20','#41B6E6'],'Norwich':         ['#00A650','#FFF200'],
  "Nott'm Forest":     ['#DD0000','#fff'],   'Sheffield United':['#EE2737','#fff'],
  'Southampton':       ['#D71920','#fff'],   'Tottenham':       ['#132257','#fff'],
  'Sunderland':        ['#EB172B','#fff'],   'Swansea':         ['#121212','#fff'],
  'Watford':           ['#FBEE23','#111'],   'West Brom':       ['#122F67','#fff'],
  'West Ham':          ['#7A263A','#1BB1E7'],'Wolves':          ['#FDB913','#231F20'],
  'Huddersfield':      ['#0E63AD','#fff'],   'Cardiff':         ['#0070B5','#fff'],
  'Stoke':             ['#E03A3E','#fff'],   'Hull':            ['#F18A00','#000'],
}

export const LOGOS = {
  'Arsenal':           '/assets/logos/arsenal.png',
  'Aston Villa':       '/assets/logos/astonvilla.png',
  'Bournemouth':       '/assets/logos/bournemouth.png',
  'Brentford':         '/assets/logos/brentford.png',
  'Brighton':          '/assets/logos/brighton.png',
  'Burnley':           '/assets/logos/burnley.png',
  'Chelsea':           '/assets/logos/chelsea.png',
  'Crystal Palace':    '/assets/logos/crystalpalace.png',
  'Everton':           '/assets/logos/everton.png',
  'Fulham':            '/assets/logos/fulham.png',
  'Ipswich':           '/assets/logos/ipswich.png',
  'Leeds':             '/assets/logos/leeds.png',
  'Leicester':         '/assets/logos/leicester.png',
  'Liverpool':         '/assets/logos/liverpool.png',
  'Luton':             '/assets/logos/luton.png',
  'Man City':          '/assets/logos/mancity.png',
  'Man United':        '/assets/logos/manutd.png',
  'Newcastle':         '/assets/logos/newcastle.png',
  "Nott'm Forest":     '/assets/logos/nottmforest.png',
  'Sheffield United':  '/assets/logos/sheffieldunited.png',
  'Southampton':       '/assets/logos/southampton.png',
  'Tottenham':         '/assets/logos/tottenham.png',
  'Sunderland':        '/assets/logos/sunderland.png',
  'Watford':           '/assets/logos/watford.png',
  'West Brom':         '/assets/logos/westbrom.png',
  'West Ham':          '/assets/logos/westham.png',
  'Wolves':            '/assets/logos/wolves.png',
  'Norwich':           '/assets/logos/norwich.png',
  'Middlesbrough':     '/assets/logos/middlesbrough.png',
  'Swansea':           '/assets/logos/swansea.png',
  'Cardiff':           '/assets/logos/cardiff.png',
  'Stoke':             '/assets/logos/stoke.png',
  'Huddersfield':      '/assets/logos/huddersfield.png',
  'Hull':              '/assets/logos/hull.png',
}

export const ABBRS = {
  'Arsenal':'ARS','Aston Villa':'AVL','Bournemouth':'BOU','Brentford':'BRE',
  'Brighton':'BHA','Burnley':'BUR','Chelsea':'CHE','Crystal Palace':'CRY',
  'Everton':'EVE','Fulham':'FUL','Ipswich':'IPS','Leeds':'LEE',
  'Leicester':'LEI','Liverpool':'LIV','Luton':'LUT','Man City':'MCI',
  'Man United':'MUN','Middlesbrough':'MID','Newcastle':'NEW','Norwich':'NOR',
  "Nott'm Forest":'NFO','Sheffield United':'SHU','Southampton':'SOU','Tottenham':'TOT',
  'Sunderland':'SUN','Swansea':'SWA','Watford':'WAT','West Brom':'WBA',
  'West Ham':'WHU','Wolves':'WOL','Huddersfield':'HUD','Cardiff':'CAR','Stoke':'STK',
  'Hull':'HUL',
}

export function getAbbr(name) {
  return ABBRS[name] || (name || '').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 3)
}

export function logoStyle(name) {
  const [bg, fg] = COLORS[name] || ['#334155', '#fff']
  return { '--team-bg': bg, '--team-fg': fg }
}
