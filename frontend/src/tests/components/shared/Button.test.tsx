import { render, fireEvent } from '../../utils/test-utils';
import { Button } from '@/components/shared/Button/Button';

describe('Button Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(
      <Button variant="primary">Click Me</Button>
    );
    
    expect(getByText('Click Me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    const { getByText } = render(
      <Button variant="primary" onClick={handleClick}>Click Me</Button>
    );
    
    fireEvent.click(getByText('Click Me'));
    expect(handleClick).toHaveBeenCalled();
  });

  it('shows loading state', () => {
    const { container } = render(
      <Button variant="primary" loading>Loading</Button>
    );
    
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('applies different variants', () => {
    const { rerender, container } = render(
      <Button variant="primary">Primary</Button>
    );
    
    expect(container.firstChild).toHaveClass('bg-emerald-600');
    
    rerender(<Button variant="secondary">Secondary</Button>);
    expect(container.firstChild).toHaveClass('bg-[#2d4a7c]');
  });
});
