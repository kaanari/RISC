library IEEE;
use IEEE.std_logic_1164.all;

entity MUX_4x1 is

	generic(
				DATA_WIDTH 	: integer := 16				
	);

	port(
			I0		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			I1		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			I2		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			I3		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			sel	: in std_logic_vector(1 downto 0);
			O		: out std_logic_vector((DATA_WIDTH-1) downto 0)
	);

end MUX_4x1;

architecture dataflow of MUX_4x1 is
begin

	with sel select
		O <=  I0 when "00",
				I1 when "01",
				I2 when "10",
				I3 when others;
				
end dataflow;