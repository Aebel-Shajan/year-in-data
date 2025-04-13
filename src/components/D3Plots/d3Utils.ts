import * as d3 from "d3";

export function createColorScale(
  ticks: number[], 
  colorScheme: readonly (readonly string[])[]
) {
  let colorRange = colorScheme[ticks.length + 1]
  colorRange = ["#EFF2F5", ...colorRange.filter((_, index) => index != 0)]
  const colorScale = d3.scaleThreshold(ticks, colorRange);
  return colorScale
}

//https://stackoverflow.com/a/13532993
export function shadeColor(color: string, percent: number) {

  let R = parseInt(color.substring(1, 3), 16);
  let G = parseInt(color.substring(3, 5), 16);
  let B = parseInt(color.substring(5, 7), 16);

  R = R * (100 + percent) / 100;
  G = G * (100 + percent) / 100;
  B = B * (100 + percent) / 100;

  R = (R < 255) ? R : 255;
  G = (G < 255) ? G : 255;
  B = (B < 255) ? B : 255;

  R = Math.round(R)
  G = Math.round(G)
  B = Math.round(B)

  const RR = ((R.toString(16).length == 1) ? "0" + R.toString(16) : R.toString(16));
  const GG = ((G.toString(16).length == 1) ? "0" + G.toString(16) : G.toString(16));
  const BB = ((B.toString(16).length == 1) ? "0" + B.toString(16) : B.toString(16));

  return "#" + RR + GG + BB;
}