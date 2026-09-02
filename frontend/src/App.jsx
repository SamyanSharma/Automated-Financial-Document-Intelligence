import { useState } from "react";
import { analyzeCompany } from "./services/api";
import "./App.css";

function App() {

    const [company, setCompany] = useState("");
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleAnalyze = async () => {

        if (!company.trim()) {
            setError("Enter a company name");
            return;
        }

        try {

            setLoading(true);
            setError("");

            const data = await analyzeCompany(company);

            setReport(data);

        } catch (err) {

            console.error(err);

            setError(
                "Unable to analyze company. Check the backend."
            );

        } finally {

            setLoading(false);

        }
    };

    return (
        <div className="app">

            <h1>
                Financial Document Intelligence
            </h1>

            <p>
                AI-powered financial document analysis
            </p>

            <div className="search-box">

                <input
                    type="text"
                    placeholder="Enter company name"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                />

                <button onClick={handleAnalyze}>
                    {loading ? "Analyzing..." : "Analyze"}
                </button>

            </div>

            {error && (
                <p className="error">
                    {error}
                </p>
            )}

            {report && (

                <div className="report">

                    <h2>
                        {report.company}
                    </h2>

                    <h3>
                        Revenue Trend
                    </h3>

                    <p>
                        {report.trend_analysis?.trend}
                    </p>

                    <h3>
                        Revenue CAGR
                    </h3>

                    <p>
                        {report.trend_analysis?.cagr}%
                    </p>

                    <h3>
                        Risk
                    </h3>

                    <p>
                        {report.risk_assessment?.risk_level}
                    </p>

                    <p>
                        Risk Score:
                        {" "}
                        {report.risk_assessment?.risk_score}/100
                    </p>

                    <h3>
                        Key Findings
                    </h3>

                    <ul>
                        {report.key_findings?.map(
                            (finding, index) => (
                                <li key={index}>
                                    {finding}
                                </li>
                            )
                        )}
                    </ul>

                </div>

            )}

        </div>
    );
}

export default App;