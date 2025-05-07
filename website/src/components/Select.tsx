const Select = (
  {
    selectedOptionIndex,
    setSelectedOptionIndex,
    options,
    defaultValue = ""
  }: {
    selectedOptionIndex: number,
    setSelectedOptionIndex: CallableFunction,
    options: string[]
    defaultValue?: string
  }
) => {

  const optionElements = options.map((option, index) => {
    return (
      <option
        value={index}
        key={String(option) + "-" + option}
      >
        {option}
      </option>
    )
  })

  return (

    <fieldset className="fieldset">
      <select
        value={selectedOptionIndex}
        onChange={e => setSelectedOptionIndex(Number(e.target.value))}
        className="select"
      >
        {defaultValue == "" ?
          <option disabled={true} value={-1}>Pick an option</option>
          :
          <option value={-1}>{defaultValue}</option>
        }
        {optionElements}
      </select>
    </fieldset>

  )
}

export default Select;