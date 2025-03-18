// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalendarLabel from 'cal-heatmap/plugins/CalendarLabel';
// @ts-expect-error cal-heatmap library don't have declration files :(
import Legend from 'cal-heatmap/plugins/Legend';
// @ts-expect-error cal-heatmap library don't have declration files :(
import Tooltip from 'cal-heatmap/plugins/Tooltip';
import 'cal-heatmap/cal-heatmap.css';
import { Dayjs } from "dayjs";

const baseOptions = {
  domain: {
    type: "month",
    gutter: 6,
    label: {
      position: 'top'
    }

  },
  subDomain: {
    type: "day",
    radius: 2,
    gutter: 3,
    label: {
      position: 'left'
    }
  },
}

const basePlugins = [
  [
    CalendarLabel,
    {
      position: 'left',
      key: 'left',
      text: () => ["", "", 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      textAlign: 'start',
      width: 30,
      padding: [0, 0, 0, 0],
    },
  ],
]

function createTooltip(unit: string) {
  return [
    Tooltip,
    {
      enabled: true,
      text: function (_timestamp: string, value: string, dayjsDate: Dayjs) {
        return `${value ? value : 0}  ${unit} || ${dayjsDate.toDate().toDateString()}`;
      }
    }
  ]
}


export function drawHeatmap({
  cal,
  itemSelector,
  data,
  valueCol,
  year,
  dateCol = 'date',
  units = 'times',
  colorDomain = [0, 30],
  colorRange = ['#9AF9A8', '#206D38'],
  groupY = "sum"
}: {
  cal: CalHeatmap,
  itemSelector: string,
  data: unknown[],
  valueCol: string,
  year: number,
  dateCol?: string,
  units?: string,
  colorDomain?: number[],
  colorRange?: string[],
  groupY?: string
}) {

  const plugins = [...basePlugins]
  plugins.push(createTooltip(units))
  plugins.push([
    Legend,
    {
      label: `${units} per day`,
      itemSelector: itemSelector + "-legend",
    },
  ])


  const options = {
    ...baseOptions,
    date: {
      start: new Date(`${year}-01-01`),
    },
    data: {
      source: data,
      x: dateCol,
      y: valueCol,
      groupY: groupY
    },
    scale: {
      color: {
        domain: colorDomain,
        range: colorRange
      }
    },
    itemSelector: itemSelector,
  }
  cal.paint(options, plugins);
}



// sort array ascending
function sortAcscending(arr: number[]) {
  return arr.sort((a, b) => a - b);
}

export function getQuantile(arr: number[], q: number) {
  q = q/100
  const sorted = sortAcscending(arr);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  } else {
    return sorted[base];
  }
};