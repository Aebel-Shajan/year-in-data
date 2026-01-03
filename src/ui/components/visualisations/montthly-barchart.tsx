import { BarChart, Legend, XAxis, YAxis, CartesianGrid, Tooltip, Bar } from 'recharts';

export default function MonthlyBarChart(
  { data }: { data: Record<string, string|number>[] }
) {
  return (
    <BarChart style={{ width: '100%', maxWidth: '700px', maxHeight: '70vh', aspectRatio: 1.618 }} responsive data={data}>
      <CartesianGrid />
      <XAxis dataKey="month" />
      <YAxis width="auto" />

      <Tooltip contentStyle={{ background: "black", borderRadius: "10px" }} />
      <Legend />
      <Bar dataKey="value" fill="#8884d8" />
    </BarChart>
  );
}
