import { render } from '../../utils/test-utils';
import { CandlestickChart } from '@/components/charts/CandlestickChart/CandlestickChart';

const mockData = [
  {
    timestamp: '2024-01-01',
    open: 100,
    high: 110,
    low: 90,
    close: 105,
    volume: 1000
  }
];

describe('CandlestickChart Component', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <CandlestickChart data={mockData} />
    );
    
    expect(container.firstChild).toBeInTheDocument();
  });

  it('displays correct axis labels', () => {
    const { getByText } = render(
      <CandlestickChart data={mockData} />
    );
    
    expect(getByText('Price')).toBeInTheDocument();
    expect(getByText('Volume')).toBeInTheDocument();
  });
});

