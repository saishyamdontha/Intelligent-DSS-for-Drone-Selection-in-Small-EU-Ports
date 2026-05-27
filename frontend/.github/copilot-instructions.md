# Drone DSS Frontend - Development Guide

This document provides coding guidelines and best practices for the Drone Selection Decision Support System frontend.

## Architecture

- **5-layer DSS**: Frontend connects to FastAPI Application Layer at http://localhost:8000/api
- **Component-based**: React components for reusable UI elements
- **Context API**: Global state management via AppContext
- **Mock-first**: All components work with mock data when backend unavailable

## Coding Standards

### TypeScript
- Use strict mode (`strict: true` in tsconfig.json)
- Define interfaces for all data types
- Use explicit return types for functions
- Avoid `any` type - use `unknown` with type guards if needed

### React
- Functional components with hooks
- Use `useCallback` for event handlers passed to children
- Use `useEffect` for side effects with proper dependency arrays
- Memoize expensive computations with `useMemo`

### File Organization
- Pages in `src/pages/` - one file per route
- Components in `src/components/` - shared, reusable
- Services in `src/services/` - API calls and business logic
- Types in `src/types/` - all TypeScript interfaces
- Context in `src/context/` - global state

### Styling
- Tailwind CSS for all styling
- Use `dark:` prefix for dark mode support
- Use semantic color names: `primary`, `secondary`, `success`, `danger`
- Maintain consistent spacing with Tailwind scale

### Component Props
- Use TypeScript interfaces for all props
- Optional props should use `?` notation
- Destructure props in function parameters
- Document complex props with JSDoc comments

## Testing with Mock Data

Mock data is in `src/services/mockData.ts`. To verify a page works:

1. Start dev server: `npm run dev`
2. Backend will be unreachable (normal)
3. App automatically uses mock data
4. Verify page renders and interactions work

## Adding New Features

1. **New Page**: Create in `src/pages/`, add route in `App.tsx`, add nav in `Layout.tsx`
2. **New Component**: Create in `src/components/`, export from there
3. **New Service Endpoint**: Add method to `src/services/api.ts` with mock fallback
4. **New Type**: Add interface to `src/types/index.ts`

## Common Tasks

### Add a new page
```typescript
// src/pages/NewPage.tsx
import { Card, Button } from '../components/FormComponents'

export default function NewPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Title</h1>
      <Card>{/* content */}</Card>
    </div>
  )
}
```

### Add a new API endpoint
```typescript
// src/services/api.ts
async getNewData() {
  try {
    const response = await this.client.get('/new-endpoint')
    return response.data
  } catch (error) {
    console.warn('Using mock data')
    return mockNewData
  }
}
```

### Use global state
```typescript
const { currentScenario, setCurrentScenario } = useAppContext()
```

### Create reusable component
```typescript
interface MyComponentProps {
  title: string
  onAction: () => void
}

export function MyComponent({ title, onAction }: MyComponentProps) {
  return <div>{/* JSX */}</div>
}
```

## Performance Optimization

- Use `React.memo()` for components that receive same props
- Implement pagination for large lists (drones, criteria)
- Lazy load pages with `React.lazy()`
- Use `useCallback` for event handlers in lists
- Debounce API calls (e.g., sensitivity analysis)

## Accessibility

- Use semantic HTML (button, form, input)
- Add aria labels where needed
- Ensure color contrast meets WCAG AA
- Support keyboard navigation
- Test with screen readers

## Common Patterns

### Conditional Rendering
```typescript
{condition && <Component />}
{condition ? <ComponentA /> : <ComponentB />}
```

### Form Handling
```typescript
const [formData, setFormData] = useState({})
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  // handle form
}
```

### API Calls
```typescript
const [loading, setLoading] = useState(false)
useEffect(() => {
  const fetchData = async () => {
    setLoading(true)
    try {
      const data = await api.getData()
      setData(data)
    } catch (error) {
      // handle error
    } finally {
      setLoading(false)
    }
  }
  fetchData()
}, [])
```

## Debugging

- Use React DevTools browser extension
- Use Redux DevTools for state inspection
- Check Network tab for API calls
- Use `console.log` or VS Code debugger
- Mock data is logged when used

## Version Info

- React: 18.2.0
- Vite: 5.0.8
- TypeScript: 5.3.3
- Node: 16+

---

**Last Updated**: May 2026
