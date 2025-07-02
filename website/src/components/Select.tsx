interface Option<T> {
  label: string;
  value: T;
}

interface SelectProps<T> {
  selectedValue: T | null;
  setSelectedValue: (value: T) => void;
  options: Option<T>[];
  labelLeft?: string;
  defaultLabel?: string;
}

export default function Select<T extends string | number>(
  {
    selectedValue,
    setSelectedValue,
    options,
    labelLeft,
    defaultLabel = "Pick an option",
  }: SelectProps<T>
) {
  return (
    <label className="select select-xs">
      {labelLeft && <span className="label">{labelLeft}</span>}
      <select
        value={selectedValue ?? ""}
        onChange={e =>
          setSelectedValue(
            typeof options[0].value === "number"
              ? (Number(e.target.value) as T)
              : (e.target.value as T)
          )
        }
        // className="select select-sm"
      >
        <option value="" disabled hidden>
          {defaultLabel}
        </option>
        {options.map((option) => (
          <option key={String(option.value)} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

    </label>
  );
}
