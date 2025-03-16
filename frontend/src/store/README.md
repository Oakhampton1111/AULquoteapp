# State Management

This directory contains the centralized state management for the application.

## Structure

```
store/
├── queries/     # React Query configurations
│   ├── quotes/    # Quote-related queries
│   ├── rates/     # Rate-related queries
│   ├── users/     # User-related queries
│   └── ai/       # AI-related queries
│       ├── chat/   # Chat service queries
│       ├── rag/    # RAG service queries
│       └── rates/  # Rate optimization queries
└── slices/      # Redux slices
    ├── auth/      # Authentication state
    ├── ui/        # UI state
    ├── form/      # Form state
    └── ai/       # AI state
        ├── chat/   # Chat service state
        ├── rag/    # RAG service state
        └── rates/  # Rate optimization state
```

## State Management Strategy

### 1. Server State (React Query)

Located in `queries/`:
```typescript
// queries/quotes/useQuotes.ts
export const useQuotes = () => {
  return useQuery({
    queryKey: ['quotes'],
    queryFn: fetchQuotes,
    staleTime: 5 * 60 * 1000,
    cacheTime: 30 * 60 * 1000,
  });
};
```

Use for:
- API data
- Caching
- Loading states
- Error handling
- Optimistic updates

### 2. Client State (Redux Toolkit)

Located in `slices/`:
```typescript
// slices/auth/authSlice.ts
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
    },
    logout: (state) => {
      state.user = null;
    },
  },
});
```

Use for:
- Global UI state
- User preferences
- Authentication
- Form state
- Navigation state

### 3. Local State (React)

Use in components:
```typescript
const [isOpen, setIsOpen] = useState(false);
const toggleOpen = useCallback(() => {
  setIsOpen(prev => !prev);
}, []);
```

Use for:
- UI interactions
- Form fields
- Animations
- Component state

## Best Practices

### 1. React Query

1. **Query Configuration**
   ```typescript
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000,
         cacheTime: 30 * 60 * 1000,
         retry: 3,
         refetchOnWindowFocus: false,
       },
     },
   });
   ```

2. **Query Keys**
   ```typescript
   // Consistent key structure
   ['entity', id, 'relation']
   ['quotes', quoteId, 'rates']
   ```

3. **Cache Management**
   ```typescript
   // Invalidate related queries
   queryClient.invalidateQueries(['quotes']);
   ```

### 2. Redux Toolkit

1. **Slice Organization**
   ```typescript
   // Feature-based slices
   auth/
   ├── authSlice.ts
   ├── selectors.ts
   └── thunks.ts
   ```

2. **Type Safety**
   ```typescript
   // Strong typing
   interface AuthState {
     user: User | null;
     loading: boolean;
     error: string | null;
   }
   ```

3. **Selectors**
   ```typescript
   // Memoized selectors
   export const selectUser = createSelector(
     [(state: RootState) => state.auth],
     (auth) => auth.user
   );
   ```

### 3. Performance

1. **Query Optimization**
   - Appropriate cache times
   - Pagination support
   - Infinite queries
   - Background updates

2. **State Updates**
   - Batch updates
   - Memoized selectors
   - Normalized state
   - Optimistic updates

3. **Memory Management**
   - Cleanup effects
   - Cache invalidation
   - State cleanup
   - Memory leaks

## Usage Guidelines

### 1. Choosing State Location

1. **Server State** (React Query)
   - API data
   - Remote data
   - Cache management
   - Real-time updates
   - LLM responses
   - RAG context
   - Rate optimization suggestions

2. **Global State** (Redux)
   - User session
   - Theme settings
   - Feature flags
   - Global UI state
   - Chat history
   - RAG context cache
   - Rate optimization settings

3. **Local State** (React)
   - Form inputs
   - Modal state
   - Toggle state
   - Animation state
   - Chat input
   - Rate optimization progress
   - Response streaming state

### 2. Data Flow

1. **Unidirectional Data Flow**
   ```typescript
   // Component
   const { data, isLoading } = useQuery(['data'], fetchData);
   const dispatch = useDispatch();
   
   // Update global state based on server response
   useEffect(() => {
     if (data) {
       dispatch(setData(data));
     }
   }, [data, dispatch]);
   ```

2. **State Updates**
   ```typescript
   // Optimistic updates
   const mutation = useMutation({
     mutationFn: updateData,
     onMutate: async (newData) => {
       await queryClient.cancelQueries(['data']);
       const previous = queryClient.getQueryData(['data']);
       queryClient.setQueryData(['data'], newData);
       return { previous };
     },
   });
   ```

### 3. Error Handling

1. **Query Errors**
   ```typescript
   const { error, isError } = useQuery(['data'], fetchData);
   
   if (isError) {
     return <ErrorComponent error={error} />;
   }
   ```

2. **Global Error State**
   ```typescript
   dispatch(setError({
     message: error.message,
     code: error.code,
   }));
   ```
