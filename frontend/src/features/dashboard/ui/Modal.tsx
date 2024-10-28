import React, { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  className,
  showCloseButton = true,
  closeOnOverlayClick = true,
  size = 'md'
}: ModalProps) {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-[90%] h-[90%]'
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog 
        as="div" 
        className="relative z-50"
        onClose={closeOnOverlayClick ? onClose : () => {}}
      >
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-50" />
        </Transition.Child>

        {/* Full-screen container for centering */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel
                className={cn(
                  'w-full transform rounded-lg bg-[#1c2c4f] p-6 text-left align-middle shadow-xl transition-all',
                  sizes[size],
                  size === 'full' && 'overflow-y-auto',
                  className
                )}
              >
                {/* Header */}
                {(title || showCloseButton) && (
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      {title && (
                        <Dialog.Title className="text-lg font-semibold text-white">
                          {title}
                        </Dialog.Title>
                      )}
                      {description && (
                        <Dialog.Description className="mt-1 text-sm text-gray-400">
                          {description}
                        </Dialog.Description>
                      )}
                    </div>
                    {showCloseButton && (
                      <button
                        type="button"
                        className="text-gray-400 hover:text-gray-300 focus:outline-none"
                        onClick={onClose}
                      >
                        <X className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className={cn(size === 'full' && 'h-full')}>
                  {children}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}

export interface ModalHeaderProps {
  className?: string;
  children: React.ReactNode;
}

export function ModalHeader({ className, children }: ModalHeaderProps) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  );
}

export interface ModalBodyProps {
  className?: string;
  children: React.ReactNode;
}

export function ModalBody({ className, children }: ModalBodyProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {children}
    </div>
  );
}

export interface ModalFooterProps {
  className?: string;
  children: React.ReactNode;
}

export function ModalFooter({ className, children }: ModalFooterProps) {
  return (
    <div className={cn('mt-6 flex justify-end space-x-4', className)}>
      {children}
    </div>
  );
}

export interface ConfirmModalProps extends Omit<ModalProps, 'children'> {
  message: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmModal({
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  variant = 'danger',
  ...props
}: ConfirmModalProps) {
  const variantStyles = {
    danger: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-yellow-600 hover:bg-yellow-700',
    info: 'bg-blue-600 hover:bg-blue-700'
  };

  return (
    <Modal {...props}>
      <ModalBody>
        <p className="text-white">{message}</p>
      </ModalBody>
      <ModalFooter>
        <button
          type="button"
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          onClick={props.onClose}
        >
          {cancelText}
        </button>
        <button
          type="button"
          className={cn(
            'px-4 py-2 text-white rounded-lg',
            variantStyles[variant]
          )}
          onClick={() => {
            onConfirm();
            props.onClose();
          }}
        >
          {confirmText}
        </button>
      </ModalFooter>
    </Modal>
  );
}

export default Modal;