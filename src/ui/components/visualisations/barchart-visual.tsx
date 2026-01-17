import { BarChart, Legend, XAxis, YAxis, Tooltip, Bar } from 'recharts';

export default function BarChartVisual(
  {
    data,
    xCol,
    yCol
  }: {
    data: Record<string, string | number>[],
    xCol: string,
    yCol: string
  }
) {
  return (
    <BarChart style={{ width: "100%", height: "100%", aspectRatio: 1.618 }} data={data} className='select-none [&>*]:outline-0'>
      <XAxis dataKey={xCol} interval={0} />
      <YAxis width="auto" />
      <Tooltip contentStyle={{ background: "black", borderRadius: "10px" }} />
      <Legend />
      <Bar dataKey={yCol} fill="#D3F3D4" />
    </BarChart>
  );
}
