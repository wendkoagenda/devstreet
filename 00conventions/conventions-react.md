# ⚛️ Conventions React

## 📁 Structure des Projets

### Organisation des Dossiers

#### Structure recommandée
- **components/** : Tous les composants React
  - **common/** : Composants UI réutilisables
  - **layout/** : Composants de mise en page
  - **features/** : Composants métier spécifiques
- **pages/** : Composants de pages
- **hooks/** : Hooks personnalisés
- **contexts/** : Contexts React
- **services/** : Services API
- **utils/** : Fonctions utilitaires
- **types/** : Types TypeScript
- **constants/** : Constantes
- **assets/** : Ressources statiques

## 🏷️ Conventions de Nommage

### Composants
```tsx
// ✅ Bon - PascalCase
const UserProfile = () => {
  return <div>Profile</div>;
};

const ProductCard = () => {
  return <div>Card</div>;
};

const NavigationMenu = () => {
  return <nav>Menu</nav>;
};

// ❌ Éviter
const userProfile = () => {};  // camelCase
const user_profile = () => {}; // snake_case
const USERPROFILE = () => {};  // UPPER_CASE
```

### Fichiers et Dossiers

#### Composants
- **Dossiers** : kebab-case (`user-profile/`, `product-card/`)
- **Fichiers** : kebab-case (`user-profile.tsx`, `user-profile.test.tsx`)
- **Fichiers de style** : kebab-case (`user-profile.module.css`)
- **Index** : `index.ts` pour les exports

#### Utilitaires
- **Dossier** : `utils/`
- **Fichiers** : camelCase (`formatDate.ts`, `validateEmail.ts`, `apiHelpers.ts`)

#### Hooks
- **Dossier** : `hooks/`
- **Fichiers** : camelCase avec préfixe `use` (`useAuth.ts`, `useLocalStorage.ts`)

#### À éviter
- PascalCase pour les dossiers (`UserProfile/`)
- snake_case (`user_profile/`)
- Tout attaché (`userprofile/`)

### Variables et Fonctions
```tsx
// ✅ Bon - camelCase
const userName = 'John Doe';
const isLoggedIn = true;
const userAge = 25;

const handleSubmit = () => {};
const validateForm = () => {};
const fetchUserData = async () => {};

// ❌ Éviter
const user_name = 'John';     // snake_case
const UserName = 'John';      // PascalCase
const USERNAME = 'John';      // UPPER_CASE
```

### Props et Interfaces
```tsx
// ✅ Bon - PascalCase avec suffixes appropriés
interface UserProfileProps {
  userId: string;
  isEditable: boolean;
  onSave: (data: UserData) => void;
}

interface UserData {
  firstName: string;
  lastName: string;
  emailAddress: string;
}

type ButtonVariant = 'primary' | 'secondary' | 'danger';

type ApiResponse<T> = {
  data: T;
  status: number;
  message: string;
};

// Composant avec props typées
const UserProfile: React.FC<UserProfileProps> = ({
  userId,
  isEditable,
  onSave
}) => {
  return <div>{/* Contenu */}</div>;
};
```

## 🎣 Hooks Personnalisés

```tsx
// ✅ Bon - Préfixe "use" + PascalCase
const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    // Logique de connexion
    setIsLoading(false);
  };
  
  return { user, isLoading, login };
};

const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });
  
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };
  
  return [storedValue, setValue] as const;
};
```
## 🔄 State Management

### useState
```tsx
const UserForm = () => {
  // ✅ Bon - Noms descriptifs
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // ✅ Bon - Objets pour les états complexes
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: ''
  });
  
  const handleInputChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };
};
```

### useReducer
```tsx
// ✅ Bon - Types et actions bien définis
type UserState = {
  users: User[];
  loading: boolean;
  error: string | null;
};

type UserAction = 
  | { type: 'FETCH_USERS_START' }
  | { type: 'FETCH_USERS_SUCCESS'; payload: User[] }
  | { type: 'FETCH_USERS_ERROR'; payload: string }
  | { type: 'ADD_USER'; payload: User }
  | { type: 'UPDATE_USER'; payload: { id: string; updates: Partial<User> } }
  | { type: 'DELETE_USER'; payload: string };

const userReducer = (state: UserState, action: UserAction): UserState => {
  switch (action.type) {
    case 'FETCH_USERS_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_USERS_SUCCESS':
      return { ...state, loading: false, users: action.payload };
    case 'FETCH_USERS_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'ADD_USER':
      return { ...state, users: [...state.users, action.payload] };
    case 'UPDATE_USER':
      return {
        ...state,
        users: state.users.map(user => 
          user.id === action.payload.id 
            ? { ...user, ...action.payload.updates }
            : user
        )
      };
    case 'DELETE_USER':
      return {
        ...state,
        users: state.users.filter(user => user.id !== action.payload)
      };
    default:
      return state;
  }
};
```

## 🌐 Context API

```tsx
// ✅ Bon - Context bien structuré
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const userData = await authService.login(credentials);
      setUser(userData);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = () => {
    setUser(null);
    authService.logout();
  };
  
  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    isLoading
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personnalisé pour utiliser le context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

## 📝 Gestion des Événements

```tsx
const UserForm = () => {
  // ✅ Bon - Noms descriptifs avec préfixe "handle"
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Logique de soumission
  };
  
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    // Logique de changement
  };
  
  const handleButtonClick = () => {
    // Logique du clic
  };
  
  const handleUserSelect = (userId: string) => {
    // Logique de sélection
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleInputChange} />
      <button type="button" onClick={handleButtonClick}>
        Cliquer
      </button>
    </form>
  );
};
```



```tsx
// user-profile.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { UserProfile } from './user-profile';

describe('UserProfile', () => {
  const mockUser = {
    id: '1',
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com'
  };
  
  it('should render user information correctly', () => {
    render(<UserProfile user={mockUser} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
  
  it('should call onEdit when edit button is clicked', () => {
    const mockOnEdit = jest.fn();
    render(<UserProfile user={mockUser} onEdit={mockOnEdit} />);
    
    fireEvent.click(screen.getByText('Modifier'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockUser.id);
  });
});
```

## 📦 Imports et Exports

```tsx
// ✅ Bon - Organisation des imports
// 1. Imports React
import React, { useState, useEffect, useCallback } from 'react';

// 2. Imports de bibliothèques tierces
import axios from 'axios';
import { format } from 'date-fns';

// 3. Imports internes (composants, hooks, utils)
import { Button } from '../common/button';
import { useAuth } from '../../hooks/useAuth';
import { formatCurrency } from '../../utils/formatters';

// 4. Imports de types
import type { User, ApiResponse } from '../../types';

// 5. Imports de styles
import styles from './user-profile.module.css';

// Export par défaut
export default UserProfile;

// Exports nommés
export { UserProfile };
export type { UserProfileProps };
```

## 🔧 Configuration et Constantes

```tsx
// constants/api.ts
export const API_ENDPOINTS = {
  USERS: '/api/users',
  PRODUCTS: '/api/products',
  ORDERS: '/api/orders'
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const;

// constants/ui.ts
export const BREAKPOINTS = {
  MOBILE: '768px',
  TABLET: '1024px',
  DESKTOP: '1200px'
} as const;

export const COLORS = {
  PRIMARY: '#007bff',
  SECONDARY: '#6c757d',
  SUCCESS: '#28a745',
  DANGER: '#dc3545',
  WARNING: '#ffc107'
} as const;
```

## 🚀 Bonnes Pratiques

1. **Utilisez TypeScript** pour un typage fort
2. **Composants fonctionnels** avec hooks plutôt que classes
3. **Props destructurées** pour une meilleure lisibilité
4. **Noms descriptifs** pour les variables et fonctions
5. **Séparation des responsabilités** : logique métier dans des hooks
6. **Mémoisation** avec useMemo et useCallback quand nécessaire
7. **Tests unitaires** pour tous les composants
8. **Gestion d'erreurs** appropriée avec Error Boundaries
9. **Accessibilité** avec les attributs ARIA appropriés
10. **Performance** : lazy loading, code splitting

## 📋 Checklist de Révision

- [ ] Noms de composants en PascalCase
- [ ] Variables et fonctions en camelCase
- [ ] Props typées avec TypeScript
- [ ] Hooks personnalisés avec préfixe "use"
- [ ] Gestionnaires d'événements avec préfixe "handle"
- [ ] Imports organisés par catégorie
- [ ] Tests unitaires présents
- [ ] Styles organisés (CSS Modules ou Styled Components)
- [ ] Gestion d'erreurs implémentée
- [ ] Accessibilité vérifiée