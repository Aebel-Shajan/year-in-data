import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type YearSelectProps = {
  value: number
  onChange: (value: number) => void
}

export function YearSelect({ value, onChange }: YearSelectProps) {
  const currentYear = new Date().getFullYear()

  const years = Array.from(
    { length: currentYear - 2023 + 1 },
    (_, i) => currentYear - i
  )

  return (
    <Select
      value={String(value)}
      onValueChange={(val) => onChange(Number(val))}
    >
      <SelectTrigger className="w-fit">
        <SelectValue placeholder="Select year" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          {years.map((y) => (
            <SelectItem key={y} value={String(y)}>
              {y}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}