library IEEE;
use IEEE.std_logic_1164.all;

entity MUX_2x1 is

	generic(
				DATA_WIDTH 	: integer := 16				
	);

	port(
			I0		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			I1		: in std_logic_vector((DATA_WIDTH-1) downto 0);
			sel	: in std_logic;
			O		: out std_logic_vector((DATA_WIDTH-1) downto 0)
	);

end MUX_2x1;

architecture dataflow of MUX_2x1 is
begin

	O <= I0 when sel = '0' else I1;

end dataflow;