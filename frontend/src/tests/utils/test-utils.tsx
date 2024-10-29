import React from 'react';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/store/slices/authSlice';
import tradingReducer from '@/store/slices/tradingSlice';

// إنشاء متجر اختبار
function createTestStore(initialState = {}) {
  return configureStore({
    reducer: {
      auth: authReducer,
      trading: tradingReducer
    },
    preloadedState: initialState
  });
}

// تغليف مخصص للاختبار
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = createTestStore();
  
  return (
    <Provider store={store}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </Provider>
  );
};

const customRender = (ui: React.ReactElement, options = {}) =>
  render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
