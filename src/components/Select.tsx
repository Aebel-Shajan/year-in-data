const Select = (
  {
    selectedOptionIndex,
    setSelectedOptionIndex,
    options,
  }: {
    selectedOptionIndex: number,
    setSelectedOptionIndex: CallableFunction,
    options: string[]
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
        <option disabled={true} value={-1}>Pick an option</option>
        {optionElements}
      </select>
    </fieldset>

  )
}

export default Select;