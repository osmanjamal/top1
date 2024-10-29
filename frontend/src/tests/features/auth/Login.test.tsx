import { render, fireEvent, waitFor } from '../../utils/test-utils';
import Login from '@/features/auth/pages/Login';

describe('Login Page', () => {
  it('renders login form', () => {
    const { getByLabelText, getByRole } = render(<Login />);
    
    expect(getByLabelText(/email/i)).toBeInTheDocument();
    expect(getByLabelText(/password/i)).toBeInTheDocument();
    expect(getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('validates form inputs', async () => {
    const { getByLabelText, getByRole, getByText } = render(<Login />);
    
    const submitButton = getByRole('button', { name: /login/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(getByText(/email is required/i)).toBeInTheDocument();
      expect(getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const { getByLabelText, getByRole } = render(<Login />);
    
    const emailInput = getByLabelText(/email/i);
    const passwordInput = getByLabelText(/password/i);
    const submitButton = getByRole('button', { name: /login/i });
    
    fireEvent.change(emailInput, {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(passwordInput, {
      target: { value: 'password123' }
    });
    
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard');
    });
  });
});
