import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ 
  className = '', 
  variant = 'default', 
  size = 'default', 
  children,
  ...props 
}, ref) => {

  // Base classes
  const baseClasses = 'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50';

  // Variant classes
  const variantClasses = {
    default: 'bg-emerald-600 text-white hover:bg-emerald-700',
    secondary: 'bg-[#2d4a7c] text-white hover:bg-[#3d5a8c]',
    outline: 'border border-gray-700 text-gray-400 hover:bg-[#2d4a7c] hover:text-white',
    ghost: 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  // Size classes
  const sizeClasses = {
    default: 'h-10 px-4 py-2',
    sm: 'h-8 px-3 py-1',
    lg: 'h-12 px-6 py-3',
    icon: 'h-9 w-9',
  };

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  return (
    <button
      className={classes}
      ref={ref}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export { Button, type ButtonProps };