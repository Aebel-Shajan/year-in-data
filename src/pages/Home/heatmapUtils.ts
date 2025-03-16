// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalendarLabel from 'cal-heatmap/plugins/CalendarLabel';
// @ts-expect-error cal-heatmap library don't have declration files :(
import Legend from 'cal-heatmap/plugins/Legend';
// @ts-expect-error cal-heatmap library don't have declration files :(
import Tooltip from 'cal-heatmap/plugins/Tooltip';
import 'cal-heatmap/cal-heatmap.css';
import * as d3 from "d3-scale-chromatic"
import { Dayjs } from "dayjs";
import { GithubData, ReadingData, SleepData, WorkoutData } from '../../types/dataTypes';


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
  date: {
    start: new Date("2024-01-01"),
  },
  theme: "dark"
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
  data,
  dateCol,
  valueCol,
  name,
  legendLabel,
  color,
  units,
  groupY="sum"
}: {
  cal: CalHeatmap,
  data: unknown[],
  dateCol: string,
  valueCol: string,
  name: string,
  legendLabel: string,
  color: { range?: string[] | unknown, scheme?: string, domain: number[] },
  units: string,
  groupY?: string
}) {
  const plugins = [...basePlugins]
  plugins.push([
    Legend,
    {
      label: legendLabel,
      itemSelector: `#${name}-legend`,
    },
  ])
  plugins.push(createTooltip(units))
  const options = {
    ...baseOptions,
    data: {
      source: data,
      x: dateCol,
      y: valueCol,
      groupY: groupY
    },
    itemSelector: `#${name}-heatmap`,
    scale: {
      color: {
        ...color,
        type: "threshold"
      }
    }
  }
  cal.paint(options, plugins);
}

export function drawWorkoutHeatmap(calH: CalHeatmap, data: WorkoutData[]) {
  drawHeatmap(
    {
      cal: calH,
      data: data,
      dateCol: "date",
      valueCol: "workout_duration_minutes",
      name: "workout",
      legendLabel: "Minutes working out",
      color: {
        scheme: "YlGnBu",
        domain: [40, 60, 80, 100],
      },
      units: "minutes",
      groupY: "max"
    }
  )
}


export function drawKindleHeatmap(cal: CalHeatmap, data: ReadingData[]) {
  drawHeatmap(
    {
      cal: cal,
      data: data,
      dateCol: "date",
      valueCol: "total_reading_minutes",
      name: "reading",
      legendLabel: "Minutes read",
      color: {
        scheme: "YlOrBr",
        domain: [20, 40, 60, 80],
      },
      units: "minutes"
    }
  )
}

export function drawGithubHeatmap(cal: CalHeatmap, data: GithubData[]) {
  drawHeatmap(
    {
      cal: cal,
      data: data,
      dateCol: "date",
      valueCol: "total_commits",
      name: "github",
      legendLabel: "Number of commits",
      color: {
        range: ["#9AE9A8", "#41C363", "#31A14E", "#206D38"],
        domain: [ 5, 10, 15, 20]
      },
      units: "commits"
    }
  )
}

export function drawSleepHeatmap(cal: CalHeatmap, data: SleepData[]) {
  drawHeatmap(
    {
      cal: cal,
      data: data,
      dateCol: "date",
      valueCol: "total_duration_hours",
      name: "sleep",
      legendLabel: "Hours slept",
      color: {
        range: d3.schemeRdBu[5],
        domain: [6, 7, 8, 9]
      },
      units: "hours"
    }
  )
}