# QRSPI Root Plan: Mathematical & Civil Engineering Specifications

This document defines the mathematical models, formulas, and programmatic algorithms implemented in the **Solar Project Intelligence Agent**, serving as the single source of truth for engineering-grade verification.

---

## 1. Land & Metric Conversions (NLC 1965)
The land office records sizes in archaic imperial units: Ekar (Acres), Rood, and Pole (Perch). The conversion to metric Hectares ($H$) and Square Meters ($S$) is modeled deterministically:

$$H = (\text{Acres} \times 0.40468564) + (\text{Roods} \times 0.10117141) + (\text{Poles} \times 0.00252928)$$

$$S = H \times 10,000.0$$

---

## 2. Civil Terrain Slope 2D Gradient (Topography)
To calculate land slope from a 2D elevation grid $z(y, x)$ with cells spaced at resolution $d$, we compute spatial finite differences in the $x$ and $y$ dimensions:

$$\frac{\partial z}{\partial x} \approx \frac{z_{i, j+1} - z_{i, j-1}}{2d}, \quad \frac{\partial z}{\partial y} \approx \frac{z_{i+1, j} - z_{i-1, j}}{2d}$$

The localized slope in radians ($\theta_{rad}$) and degrees ($\theta_{deg}$) at cell $(i, j)$ is:

$$\theta_{rad} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right)$$

$$\theta_{deg} = \theta_{rad} \times \frac{180.0}{\pi}$$

### CAPEX Earthworks Retention Cost Premium Multiplier ($M_{grading}$)
$$\begin{cases} 
1.35 & \text{if } \max(\theta_{deg}) \ge 30.0^\circ \quad \text{(High landslide risk)} \\
1.15 & \text{if } \text{count}(\theta_{deg} > 15.0^\circ) / N \ge 0.20 \quad \text{(Medium grading required)} \\
1.00 & \text{otherwise} \quad \text{(Optimal flat terrain)}
\end{cases}$$

---

## 3. Single-Line Diagram $\epsilon$-Distance Neighbor Search
To map visual component nodes ($V$) to wiring vector segment endpoints ($pt_1, pt_2$), we find the Euclidean distance $D(pt, bbox)$ between the line endpoint and the bounding box. The distance is defined as 0 if the point is inside the box, or the shortest distance to any of the 4 boundaries:

$$D(pt, bbox) \le \epsilon \quad (\text{where } \epsilon = 15.0 \text{ pixels})$$

If $D(pt_1, v_i) \le \epsilon$ and $D(pt_2, v_j) \le \epsilon$, we add a directed edge $(v_i, v_j)$ in our NetworkX graph. The grid-code verifier then runs:

$$\text{assert } \exists \text{ path } P = (v_{transformer}, \dots, v_{grid})$$
$$\text{assert } \exists v_{islanding} \in V$$

---

## 4. Tropical Solar Sizing & Financial Engine

### A. Sizing
Given a metric land area $S$, setbacks remove 10% for buffers ($S_{usable} = S \times 0.90$). The DC capacity ($P_{dc}$ in MWp) is sized based on standard spacing of 3 acres (12,140 sqm) per MWp:

$$P_{dc} = \frac{S_{usable}}{12,140}$$

### B. Temperature-Derated Energy Yield
In tropical environments, cell operating temperatures easily exceed STC ($25^\circ\text{C}$), causing cell power drop. We apply a cell temperature loss coefficient ($C_{temp} = 0.88$, or 12% loss) and a performance ratio ($PR = 0.78$):

$$E_{yr1} = P_{dc} \times 1,000.0 \times \text{GHI} \times PR \times C_{temp}$$

### C. Cash Flows & Degradation
Annual PV module performance degrades by $0.5\%$ ($d = 0.005$) annually. OPEX ($O$) inflates at $2.0\%$ ($i = 0.02$) annually:

$$E_{yr\_t} = E_{yr1} \times (1 - d)^{t-1}$$

$$O_t = (\text{Base OPEX}) \times (1 + i)^{t-1}$$

$$\text{CashFlow}_t = (E_{yr\_t} \times \text{Tariff}) - O_t$$

### D. Levelized Cost of Electricity (LCOE)
The LCOE (RM/kWh) is solved over the project lifetime ($L = 21$ years) using the Weighted Average Cost of Capital ($WACC = 0.065$):

$$\text{LCOE} = \frac{\text{CAPEX}_{adjusted} + \sum_{t=1}^{L} \frac{O_t}{(1 + WACC)^t}}{\sum_{t=1}^{L} \frac{E_{yr\_t}}{(1 + WACC)^t}}$$

### E. Net Present Value (NPV)
$$\text{NPV} = -\text{CAPEX}_{adjusted} + \sum_{t=1}^{L} \frac{\text{CashFlow}_t}{(1 + WACC)^t}$$

### F. Internal Rate of Return (IRR) Solver
Solved iteratively using the **Newton-Raphson method**:

$$r_{n+1} = r_n - \frac{f(r_n)}{f'(r_n)}$$

$$\text{where } f(r) = -\text{CAPEX}_{adjusted} + \sum_{t=1}^{L} \frac{\text{CashFlow}_t}{(1 + r)^t}$$

$$f'(r) = \sum_{t=1}^{L} \frac{-t \times \text{CashFlow}_t}{(1 + r)^{t+1}}$$
