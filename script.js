// Configuration of themes (Background colors for segments)
const themes = {
  'theme-gray': ['#4a4a4a', '#454545', '#3e3e3e', '#383838', '#323232', '#2c2c2c', '#252525', '#1f1f1f', '#0e1017'],
  'theme-aurora': ['#1e2a4a', '#252b4b', '#2d2c4b', '#342d4c', '#3c2d4d', '#432e4e', '#4b2f4e', '#52304f', '#0e1017'],
  'theme-sunset': ['#241f42', '#2c2142', '#352442', '#3d2642', '#452942', '#4d2b42', '#562e41', '#5e3041', '#0e1017'],
  'theme-forest': ['#163a34', '#193a39', '#1c3a3d', '#1f3a42', '#233a47', '#263a4c', '#293a50', '#2c3a52', '#0e1017']
};

// Data for the segments
const segmentsData = [
  { text: 'ccspace', color: '#88c0d0' },
  { text: 'main', color: '#ecc487', sub: ' ↑2', subColor: '#a3be8c' },
  { text: '+128', color: '#a3be8c', sub: ' -34', subColor: '#e06c75', sub2: ' ?1', subColor2: '#9aa5c4' },
  { text: 'Opus', color: '#c5a8d8', sub: ' · xhigh', subColor: '#968cb9' },
  { text: 'ctx 18%', color: '#a3be8c' },
  { text: '53m', color: '#9aa5c4', sub: ' · $8.02', subColor: '#ebcb8b' },
  { text: 'you', color: '#d08770' },
  { text: '5h ', color: '#9aa5c4', sub: '18%', subColor: '#a3be8c', sub2: ' · 7d 87%', subColor2: '#e06c75' }
];

// State
let currentLayout = 'one-line'; // 'one-line' | 'two-lines'
let currentStyle = 'powerline'; // 'powerline' | 'plain'
let currentTheme = 'theme-gray';

// DOM Elements
const container = document.getElementById('statusline-container');
const titleState = document.getElementById('title-state');

// Initial Render
renderStatusLine();
updateTitleState();

// Event Listeners
document.querySelectorAll('#layout-options .option-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('#layout-options .option-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    currentLayout = e.target.dataset.value;
    renderStatusLine();
    updateTitleState();
  });
});

document.querySelectorAll('#style-options .option-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('#style-options .option-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    currentStyle = e.target.dataset.value;
    container.className = `statusline-container ${currentLayout} ${currentStyle} ${currentTheme}`;
    renderStatusLine();
    updateTitleState();
  });
});

document.querySelectorAll('#theme-options .theme-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const target = e.target.closest('.theme-btn');
    document.querySelectorAll('#theme-options .theme-btn').forEach(b => b.classList.remove('active'));
    target.classList.add('active');
    currentTheme = target.dataset.value;
    container.className = `statusline-container ${currentLayout} ${currentStyle} ${currentTheme}`;
    renderStatusLine();
    updateTitleState();
  });
});

function updateTitleState() {
  const layoutText = currentLayout === 'one-line' ? '1 line' : '2 lines';
  const styleText = currentStyle;
  const themeText = currentTheme.replace('theme-', '');
  titleState.textContent = `${themeText} · ${styleText} · ${layoutText}`;
}

function renderStatusLine() {
  container.innerHTML = '';
  const colors = themes[currentTheme];
  
  if (currentLayout === 'one-line') {
    container.appendChild(createRow(0, segmentsData.length, colors));
  } else {
    // 2 lines layout: split at index 6
    container.appendChild(createRow(0, 6, colors));
    
    // Create new color array for second line to start from beginning of theme
    const secondRowColors = [...colors];
    container.appendChild(createRow(6, segmentsData.length, secondRowColors));
  }
}

function createRow(startIndex, endIndex, colors) {
  const row = document.createElement('div');
  row.className = 'status-row';
  
  const statusLine = document.createElement('div');
  statusLine.className = 'status-line';
  
  for (let i = startIndex; i < endIndex; i++) {
    const data = segmentsData[i];
    const isLast = (i === endIndex - 1);
    const bgColor = colors[i - startIndex];
    const nextBgColor = colors[i - startIndex + 1];
    
    // Segment content
    const seg = document.createElement('div');
    seg.className = 'seg';
    if (currentStyle === 'powerline') seg.style.background = bgColor;
    
    let content = `<span class="lead" style="color: ${data.color};">${data.text}</span>`;
    if (data.sub) content += `<span style="color: ${data.subColor};">${data.sub}</span>`;
    if (data.sub2) content += `<span style="color: ${data.subColor2};">${data.sub2}</span>`;
    seg.innerHTML = content;
    
    statusLine.appendChild(seg);
    
    // Divider
    if (currentStyle === 'powerline') {
      const arrow = document.createElement('div');
      arrow.className = 'arrow';
      arrow.style.background = nextBgColor; // Container takes next color
      
      const arrowInner = document.createElement('i');
      arrowInner.style.background = bgColor; // Inner arrow takes current color
      arrow.appendChild(arrowInner);
      
      statusLine.appendChild(arrow);
    } else if (!isLast) {
      // Plain style chevron
      const chev = document.createElement('span');
      chev.className = 'chev';
      chev.textContent = '›';
      statusLine.appendChild(chev);
    }
  }
  
  row.appendChild(statusLine);
  return row;
}
