import { render, screen } from "@testing-library/react";

import HomePage from "../app/page";

describe("HomePage", () => {
  it("renders the hero copy", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Merak Trip Planner");
    expect(
      screen.getByText(/web client is under active development/i),
    ).toBeInTheDocument();
  });
});
