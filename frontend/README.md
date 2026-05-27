# Drone Selection Decision Support System - Frontend

A modern React + Vite web application for intelligently selecting drones using the TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) multi-criteria decision-making methodology combined with AHP (Analytic Hierarchy Process) pairwise comparisons.

## Features

✨ **5-Page Workflow**
- **Setup Page** - Configure port parameters (budget, mission type, environment)
- **Criteria Weighting** - AHP pairwise comparison matrix (20 criteria)
- **Results & Rankings** - TOPSIS-based drone rankings with visualizations
- **Sensitivity Analysis** - Real-time weight adjustment with impact analysis
- **Comparison Table** - Side-by-side drone specs with color-coded performance

🎨 **Modern UI/UX**
- Dark mode support with persistent theme
- Responsive design (mobile, tablet, desktop)
- Progress stepper showing workflow completion
- Sidebar navigation with real-time highlighting
- Tailwind CSS for styling

📊 **Data Visualizations**
- Bar chart: Top 5 drones by TOPSIS score
- Radar chart: Top 3 drones across key criteria
- Line chart: Sensitivity analysis with weight adjustments
- Interactive expandable rows for full specifications

🔗 **API Integration**
- FastAPI backend support at `http://localhost:8000/api`
- Mock data fallback for standalone preview
- Comprehensive error handling
- Mock endpoints for all operations

## Tech Stack

- **Frontend Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + PostCSS
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Charts**: Recharts
- **Icons**: Lucide React

## Installation

### Prerequisites
- Node.js 16+ and npm/yarn

### Setup

1. **Clone/Extract the project**
```bash
cd drone-dss-frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

The app will open automatically at `http://localhost:5173`

## Usage

### Workflow

1. **Setup Scenario** (`/setup`)
   - Enter scenario name
   - Set budget range (min/max sliders)
   - Select mission type (surveillance, inspection, environmental monitoring, maritime safety)
   - Choose environment type (coastal, inland, mixed)
   - Click "Continue to Criteria Weighting"

2. **Weight Criteria** (`/criteria`)
   - Rate 20 criteria pairs using Saaty scale (1-9)
   - Higher values indicate first criterion is more important
   - Matrix automatically calculates reciprocal values
   - Submit to calculate AHP weights and proceed to evaluation

3. **Review Results** (`/results`)
   - View TOPSIS rankings with closeness coefficient scores
   - Expand drone rows to see full specifications
   - Analyze top 5 drones via bar chart
   - Compare top 3 drones via radar chart
   - Sort by rank, score, or name

4. **Sensitivity Analysis** (`/sensitivity`)
   - Adjust individual criterion weights using sliders
   - Watch live impact on top 3 drones
   - Line chart shows ranking changes with weight shifts
   - Reset to equal weights anytime

5. **Compare Drones** (`/compare`)
   - Select multiple drones for side-by-side comparison
   - Color-coded cells: green = best, red = worst per criterion
   - Export comparison to PDF (in production)
   - Add/remove drones dynamically

### Mock Data Mode

When the backend is unavailable, the app uses built-in mock data:
- 5 sample drones with realistic specifications
- 20 evaluation criteria with categories
- Sample results with TOPSIS scores
- Complete pairwise comparison matrix

To enable mock mode, start the app without a running backend:
```bash
npm run dev
# Backend unavailable? Mock data will be used automatically
```

## API Endpoints

The frontend connects to these FastAPI endpoints:

### Scenario Management
- `GET /api/scenarios` - List all scenarios
- `POST /api/scenarios` - Create new scenario

### Drone Data
- `GET /api/drones` - Get all drone specifications

### Criteria
- `GET /api/criteria` - Get evaluation criteria
- `POST /api/criteria/pairwise` - Submit AHP pairwise matrix

### Evaluation
- `POST /api/evaluate` - Run TOPSIS evaluation
- `GET /api/results/{id}` - Get scenario results
- `POST /api/sensitivity/{id}` - Sensitivity analysis

## Configuration

### API URL

Edit `src/services/api.ts` to change the API base URL:

```typescript
const API_BASE_URL = 'http://your-backend-url:8000/api'
```

### Theme Colors

Customize colors in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#0066cc',    // Main brand color
      secondary: '#00cc99',  // Accent color
    },
  },
}
```

## Development

### Project Structure

```
src/
├── pages/               # Route pages (Setup, Criteria, Results, etc.)
├── components/          # Reusable UI components (Layout, FormComponents)
├── services/            # API service and mock data
├── context/             # AppContext for global state
├── types/              # TypeScript type definitions
├── App.tsx             # Main router component
├── main.tsx            # Entry point
└── index.css           # Global styles
```

### Scripts

```bash
npm run dev       # Start dev server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

### Adding New Pages

1. Create page component in `src/pages/`
2. Import in `src/App.tsx`
3. Add route in `Routes`
4. Link in sidebar in `src/components/Layout.tsx`

## Styling Guide

- **Tailwind CSS classes** - Primary styling method
- **Dark mode** - Use `dark:` prefix for dark theme classes
- **Responsive** - Use `md:` and `lg:` prefixes for breakpoints
- **Components** - Use `Card`, `Button`, `FormField` from `FormComponents.tsx`

## Browser Support

- Chrome/Edge 88+
- Firefox 87+
- Safari 14+

## Troubleshooting

### Port already in use
```bash
# Use different port
npm run dev -- --port 5174
```

### Module not found errors
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Dark mode not working
- Check browser DevTools - ensure `dark` class on `<html>`
- localStorage should have `theme: 'dark'`

### API errors
- Verify backend is running at configured URL
- Check CORS headers on backend
- App uses mock data as fallback

## Performance Tips

- Lazy load pages for production build
- Implement pagination for large drone/criteria lists
- Memoize expensive computations
- Use React DevTools Profiler to find bottlenecks

## License

MIT

## Support

For issues or feature requests, contact the development team or submit via the backend system.

---

**Version**: 1.0.0  
**Last Updated**: May 2026  
**Built with**: React 18, Vite, Tailwind CSS
